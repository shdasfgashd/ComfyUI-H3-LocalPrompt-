"""Local sampled-frame analysis and H3 prompt authoring. No inference API."""
import gc
import json
import math
from pathlib import Path


def sample_indices(count, limit):
    if count < 1:
        raise ValueError('参考视频没有帧，请启用视频节点并重新上传视频。')
    n = min(count, limit)
    return [round(i * (count - 1) / max(1, n - 1)) for i in range(n)]


class H3LocalVideoPrompt:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'frames': ('IMAGE',),
            'source_duration': ('FLOAT', {'forceInput': True}),
            'target_duration': ('FLOAT', {'forceInput': True}),
            'model_folder': ('STRING', {'default': 'Qwen3-VL-4B-Instruct'}),
            'device': (['cpu', 'cuda'],),
            'max_frames': ('INT', {'default': 12, 'min': 2, 'max': 48}),
            'max_side': ('INT', {'default': 448, 'min': 224, 'max': 896}),
            'max_new_tokens': ('INT', {'default': 1400, 'min': 128, 'max': 4096}),
            'transcribe': ('BOOLEAN', {'default': False}),
            'whisper_folder': ('STRING', {'default': 'faster-whisper-small'}),
            'direction': ('STRING', {'multiline': True, 'default': 'Write an English video generation prompt. Preserve observed shot order, motion and pacing. No subtitles or watermarks.'}),
        }, 'optional': {'audio': ('AUDIO',), 'product_image': ('IMAGE',)}}

    RETURN_TYPES = ('STRING', 'STRING')
    RETURN_NAMES = ('h3_prompt', 'analysis_report')
    FUNCTION = 'analyze'
    CATEGORY = 'H3/Local Prompt'

    def analyze(self, frames, source_duration, target_duration, model_folder, device,
                max_frames, max_side, max_new_tokens, transcribe, whisper_folder,
                direction, audio=None, product_image=None):
        import numpy as np
        import torch
        import folder_paths
        from PIL import Image
        from transformers import AutoProcessor, Qwen3VLForConditionalGeneration
        if source_duration <= 0 or target_duration <= 0:
            raise ValueError('视频时长必须大于 0。')
        if device == 'cuda' and not torch.cuda.is_available():
            raise RuntimeError('CUDA 不可用，请选择 cpu。')
        base = Path(folder_paths.models_dir) / 'LLM'
        path = Path(model_folder)
        path = path if path.is_absolute() else base / path
        if not (path / 'config.json').is_file():
            raise FileNotFoundError(f'请先下载完整 Hugging Face 模型目录到 {path}；H3 CLIP 编码器不能替代此模型。')
        ids = sample_indices(len(frames), max_frames)
        transcript = 'Audio was not analyzed. Do not infer original dialogue, music or sound effects.'
        if transcribe:
            if audio is None:
                raise ValueError('开启转写需要连接参考视频的 audio 输出。')
            from faster_whisper import WhisperModel
            from scipy.signal import resample_poly
            wp = Path(whisper_folder)
            wp = wp if wp.is_absolute() else base / wp
            if not (wp / 'model.bin').is_file():
                raise FileNotFoundError(f'缺少本地 Whisper 模型：{wp}')
            waveform = audio['waveform'].detach().float().cpu()
            if waveform.ndim != 3 or waveform.shape[0] != 1:
                raise ValueError('Whisper 需要 AUDIO waveform [1, channels, samples]。')
            mono = waveform[0].mean(0).numpy()
            rate = int(audio['sample_rate'])
            gcd = math.gcd(rate, 16000)
            mono = resample_poly(mono, 16000 // gcd, rate // gcd).astype(np.float32)
            wm = WhisperModel(str(wp), device='cpu', compute_type='int8', local_files_only=True)
            try:
                segments, info = wm.transcribe(mono, beam_size=5, vad_filter=True)
                lines = [f'{s.start:.2f}-{s.end:.2f}s: {s.text}' for s in segments]
                transcript = f'ASR language={info.language}; may contain errors; verify quotes.\n' + '\n'.join(lines)
            finally:
                del wm
                gc.collect()
        def pil(tensor):
            a = (tensor.detach().float().cpu().clamp(0, 1).numpy()[..., :3] * 255).round().astype(np.uint8)
            im = Image.fromarray(a)
            im.thumbnail((max_side, max_side))
            return im
        content = []
        times = []
        for i in ids:
            t = i * source_duration / len(frames)
            times.append(round(t, 3))
            content.extend([{'type': 'text', 'text': f'Reference video frame at {t:.3f} seconds:'},
                            {'type': 'image', 'image': pil(frames[i])}])
        if product_image is not None:
            content.extend([{'type': 'text', 'text': 'Separate product reference, NOT a video frame. Preserve its geometry, camera/indicator placement, frame color and temple shape. Do not invent capabilities.'},
                            {'type': 'image', 'image': pil(product_image[0])}])
        instruction = f'''You are a video analyst and MiniMax H3 prompt writer. Analyze the ordered sampled frames.
Source clip duration: {source_duration:.3f}s. Requested output duration: {target_duration:.3f}s.
Sampling misses brief actions and cuts: mark uncertainty; never claim exact continuous motion or precise cuts without evidence.
Never infer nationality, identity, dialogue or sound from appearance. ASR is fallible.
Audio evidence: {transcript}
User creative direction (adaptation, not evidence): {direction}
Return ONLY a JSON object with two string keys: analysis_report and h3_prompt.
analysis_report: explain in Chinese visible subjects, environment, lighting, shot sizes, camera movement with uncertainty, ordered action timeline, audio evidence limits, and any adaptations.
h3_prompt: concise professional English generation instructions: reference use, subjects, environment, shot sizes, camera motion, chronological timed actions fitting output duration, continuity, lighting, performance and audio direction. Scale observed timing to requested output duration. Include dialogue only if supported by ASR or explicitly requested by user; label invented dialogue in report. Treat subtitle text as visual text, not proof of speech. Avoid unsupported product specs. Refer to the first connected reference video and separate product image in plain language; do not invent model-specific media tag syntax. No markdown, no analysis inside h3_prompt.'''
        content.append({'type': 'text', 'text': instruction})
        model = processor = inputs = outputs = None
        try:
            if device == 'cuda':
                import comfy.model_management as mm
                mm.unload_all_models()
                mm.soft_empty_cache()
            dtype = torch.float32 if device == 'cpu' else (torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16)
            processor = AutoProcessor.from_pretrained(str(path), local_files_only=True)
            model = Qwen3VLForConditionalGeneration.from_pretrained(str(path), torch_dtype=dtype,
                        attn_implementation='sdpa', local_files_only=True).to(device).eval()
            inputs = processor.apply_chat_template([{'role': 'user', 'content': content}],
                        tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors='pt').to(device)
            with torch.inference_mode():
                outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
            raw = processor.batch_decode(outputs[:, inputs['input_ids'].shape[1]:], skip_special_tokens=True)[0].strip()
            start, end = raw.find('{'), raw.rfind('}')
            try:
                result = json.loads(raw[start:end + 1])
                prompt, report = result['h3_prompt'], result['analysis_report']
                if not isinstance(prompt, str) or not prompt.strip() or not isinstance(report, str):
                    raise ValueError('Missing string fields')
            except (ValueError, KeyError, TypeError) as exc:
                raise RuntimeError('模型返回格式不完整，请提高 max_new_tokens 或减少抽帧数量。输出前 800 字：' + raw[:800]) from exc
            report += '\n\nSampling metadata: ' + json.dumps({'frame_indices': ids, 'timestamps_seconds': times, 'source_duration': source_duration, 'target_duration': target_duration}, ensure_ascii=False)
            return (prompt.strip(), report)
        finally:
            del outputs, inputs, model, processor
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


class H3PromptReview:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'generated_prompt': ('STRING', {'forceInput': True}),
                'analysis_report': ('STRING', {'forceInput': True}),
                'manual_override': ('STRING', {'multiline': True, 'default': ''})}}
    RETURN_TYPES = ('STRING',)
    RETURN_NAMES = ('final_prompt',)
    FUNCTION = 'review'
    CATEGORY = 'H3/Local Prompt'
    OUTPUT_NODE = True
    def review(self, generated_prompt, analysis_report, manual_override):
        text = manual_override.strip() or generated_prompt
        return {'ui': {'text': [text, analysis_report]}, 'result': (text,)}


NODE_CLASS_MAPPINGS = {'H3LocalVideoPrompt': H3LocalVideoPrompt, 'H3PromptReview': H3PromptReview}
NODE_DISPLAY_NAME_MAPPINGS = {'H3LocalVideoPrompt': 'H3 本地视频分析 · Qwen3-VL', 'H3PromptReview': 'H3 提示词预览 / 手动覆盖'}
WEB_DIRECTORY = './web'
