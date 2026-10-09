# MiniMax H3 本地视频分析升级包

本包基于你上传的工作流生成，包含真实自定义节点代码，不能只导入 JSON 而跳过安装节点。

## 文件
- H3_Local_Analyze_Only.json：先分析并预览，不执行 H3 生成。建议首次使用此版本。
- H3_Local_Auto.json：自动分析 → 提示词预览/覆盖 → H3 生成。
- ComfyUI-H3-LocalPrompt/：放进 ComfyUI/custom_nodes/ 的完整节点目录。

## Windows 便携版安装
先关闭 ComfyUI。在 ComfyUI_windows_portable 目录打开命令行。将本包的 ComfyUI-H3-LocalPrompt 文件夹复制到 ComfyUI/custom_nodes/ 下，然后执行：

```bat
python_embeded\python.exe -m pip install -r ComfyUI\custom_nodes\ComfyUI-H3-LocalPrompt\requirements.txt
python_embeded\python.exe ComfyUI\custom_nodes\ComfyUI-H3-LocalPrompt\download_models.py --comfy-root ComfyUI
```

如果要识别原视频台词，再执行：

```bat
python_embeded\python.exe -m pip install -r ComfyUI\custom_nodes\ComfyUI-H3-LocalPrompt\requirements-audio.txt
python_embeded\python.exe ComfyUI\custom_nodes\ComfyUI-H3-LocalPrompt\download_models.py --comfy-root ComfyUI --audio
```

这是节点安装包，不包含体积较大的模型权重，也不是 Windows 独立软件安装器。首次安装依赖和下载模型需要联网；之后识别代码使用 local_files_only=True，不调用云端 API。模型下载可以在另一台电脑完成，再复制完整目录。

如果使用 Desktop、虚拟环境或其他整合包，请使用该 ComfyUI 实际运行的 Python 执行 pip 和下载脚本，不能直接套用便携版路径。已有 torch 由 ComfyUI 环境提供，本包不会额外安装另一套 torch。

## 使用顺序
1. 重启 ComfyUI，刷新浏览器，导入 H3_Local_Analyze_Only.json。
2. 在 143 号 LoadVideoUI 重新选择你的本地参考视频。JSON 中原视频文件名只是占位，不包含视频文件。确认裁剪范围和时长。
3. 在 139 号原参考图片节点重新选择产品图；该图同时供 H3 和分析器使用。确认它确实是产品图。若不需要产品图，断开分析器的 product_image 连接，并相应调整 direction。
4. 132 号仍控制目标视频秒数；保留原值 15 秒。原 H3 的帧数公式会向合法帧数取整，实际输出时长可能略有差异。
5. 点击运行，在 187 号查看英文提示词和中文分析报告。可以复制英文文本进行修改。
6. 导入 H3_Local_Auto.json，重新确认参考视频和所有原模型、图片、音频文件存在。把修改后的完整提示词粘贴进 manual_override；留空则使用自动生成结果。点击运行即继续 H3 生成。

预览节点不是运行过程中的暂停/审批点。自动版一次运行会继续生成；要先审核，请使用仅分析版。手动覆盖仍会执行上游分析；它不会绕过 Qwen 加载。

## 新连线
143.images → 186.frames（使用缩放前的原帧）
143.duration → 186.source_duration
132.FLOAT → 186.target_duration
143.audio → 186.audio（仅 transcribe=true 时用于转写）
139.IMAGE → 186.product_image
186.h3_prompt / analysis_report → 187
187.final_prompt → 136.prompt

保留原 143 → 144 → 136 的视频参考路线。原 138 号长手写提示词完整保留为断开的备份。
原文件 143.mode=4（旁路），自动版和仅分析版改为启用 mode=0。
仅分析版将其余 H3 生成分支 mode=2 禁用，避免触发生成模型加载。
保留原 H3 模型、LoRA、采样参数、分辨率、音频参考和输出路线。

## 本地模型与资源
默认独立模型：Qwen3-VL-4B-Instruct。原 CLIPLoader 的 Qwen 编码器不能充当本节点的生成式视觉语言模型。
默认 device=cpu，兼容没有可用额外显存的环境，但 4B 模型 CPU 分析可能很慢，且需要足够系统内存。CPU float32 权重仅参数就约 16GB，连同原工作流和推理开销，建议至少 32GB RAM，实际需要可能更高。
有独立 NVIDIA 显存余量可改 cuda：bf16/fp16 参数约 8GB，加上视觉输入、上下文和推理缓存需更多；12–16GB 显存只是经验起点，不能保证。默认 12 帧 / 最长边 448；显存不足先减至 6–8 帧和 336。程序不自动量化或多设备切分。
选择 CUDA 时会先请求 ComfyUI 卸载已有模型，再加载 Qwen；最后释放 Qwen。这能降低竞争，但不能保证工作流调度期间完全避免显存重叠。
模型目录：ComfyUI/models/LLM/Qwen3-VL-4B-Instruct。也可以在 model_folder 填完整绝对路径。
可选 Whisper 模型目录：ComfyUI/models/LLM/faster-whisper-small，CPU int8 转写，不使用付费 API。

## 识别边界
本节点将均匀抽取的多张帧及时间戳交给 Qwen，是抽帧序列理解，不是逐帧光流分析；可能漏掉快速动作、短镜头、过渡和短暂出现的物体。时间以截取片段的起点为 0，依赖 LoadVideoUI 的帧序列和 duration 对齐；不包含裁剪前的绝对时间。
默认 transcribe=false：分析画面，不识别原台词、音乐、环境音。开启后使用参考视频 audio 做本地语音转写；Whisper 不是音乐/音效分类器，台词仍需核对。
提示词包含时序、动作、运镜、光线、连贯性和创作约束，不保证生成模型精确执行，也不保证产品结构百分之百复原。
媒体标签取决于用户已安装 H3 扩展的实现。本包不写死未经确认的 <Video 0>/<Video 1>/<Product Image 1> 标签，使用普通语言描述已连接参考素材。如你确定自己的 H3 节点要求特定标签，可在 direction 明确要求或在 manual_override 添加。
本包没有你的显卡、ComfyUI 或 H3 权重运行环境；验证范围是 JSON 连线、节点接口、模式和辅助逻辑，未做真实 Qwen 推理或 H3 视频生成测试。

## 常见错误
- 缺少 H3LocalVideoPrompt / H3PromptReview：检查节点目录层级、依赖安装到正确 Python、重启日志。
- transformers 找不到 Qwen3VLForConditionalGeneration：检查该环境的 transformers 版本，要求支持 Qwen3-VL；安装前可备份现有环境以便处理其他插件依赖冲突。
- 模型目录缺 config.json：必须下载完整 Hugging Face 模型及 processor/tokenizer 文件，不能仅放一个 safetensors。
- CUDA out of memory：降低抽帧和分辨率，或改 CPU 并确保内存足够。
- 返回 JSON 不完整：增加 max_new_tokens，或减少抽帧、缩短 direction。
- 原有 LoadVideoUI / LayerStyle / H3 节点缺失：本包依赖你原工作流已有扩展，不包含那些原插件。

## 官方参考
https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct
https://github.com/SYSTRAN/faster-whisper
https://docs.comfy.org/custom-nodes/backend/server_overview
