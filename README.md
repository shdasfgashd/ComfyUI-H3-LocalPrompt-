# ComfyUI-H3-LocalPrompt-
ComfyUI-H3-LocalPrompt。
# ComfyUI-H3-LocalPrompt

通过本地 Qwen3-VL 分析参考视频，自动生成适用于 MiniMax H3 的英文提示词，并直接接入 ComfyUI 视频生成工作流。

支持中文分析报告、英文分镜提示词、产品参考图、手动修改提示词，以及可选的本地语音转写。

> 当前为实验性初版：已检查工作流连线和节点接口，尚未完成真实 Qwen3-VL 推理及 H3 视频生成的端到端测试。

## 功能

- 从参考视频均匀抽帧，分析人物、环境、动作、光线及镜头变化。
- 根据目标视频时长生成英文分镜提示词。
- 输出中文分析报告，说明识别结果和不确定内容。
- 支持产品图片参考，要求保持产品外观和结构。
- 提供提示词预览和完整手动覆盖。
- 可选 faster-whisper 本地台词转写。
- 模型下载完成后，识别过程不调用云端 API。

## 节点

| 节点标识 | 显示名称 | 功能 |
|---|---|---|
| `H3LocalVideoPrompt` | H3 本地视频分析 · Qwen3-VL | 分析视频并生成提示词 |
| `H3PromptReview` | H3 提示词预览 / 手动覆盖 | 显示结果并输出最终提示词 |

## 仓库目录

```text
ComfyUI-H3-LocalPrompt/
├── __init__.py
├── download_models.py
├── requirements.txt
├── requirements-audio.txt
├── README.md
├── web/
│   └── preview.js
└── workflows/
    ├── H3_Local_Analyze_Only.json
    └── H3_Local_Auto.json
```

`__init__.py` 必须位于节点文件夹的根目录，不能再套一层文件夹。

## 安装

### 方法一：Git 克隆

在 `ComfyUI/custom_nodes` 目录打开终端，执行：

```bash
git clone https://github.com/shdasfgashd/ComfyUI-H3-LocalPrompt-.git ComfyUI-H3-LocalPrompt
```

命令最后的 `ComfyUI-H3-LocalPrompt` 指定本地文件夹名称，后续安装路径均使用这个名称。

### 方法二：下载 ZIP

1. 在 GitHub 仓库点击 **Code → Download ZIP**。
2. 解压，将节点文件夹重命名为 `ComfyUI-H3-LocalPrompt`。
3. 放入 `ComfyUI/custom_nodes/`。
4. 确认存在：

```text
ComfyUI/custom_nodes/ComfyUI-H3-LocalPrompt/__init__.py
```

### 安装 Python 依赖

如果使用 Windows ComfyUI 便携版，在 `ComfyUI_windows_portable` 目录打开 CMD，执行：

```bat
python_embeded\python.exe -m pip install -r ComfyUI\custom_nodes\ComfyUI-H3-LocalPrompt\requirements.txt
```

如果需要识别原视频台词，再安装：

```bat
python_embeded\python.exe -m pip install -r ComfyUI\custom_nodes\ComfyUI-H3-LocalPrompt\requirements-audio.txt
```

其他安装方式请使用 **ComfyUI 实际运行的 Python 环境**执行上述安装，不能直接套用便携版路径。

安装后完全重启 ComfyUI，并刷新浏览器。

> 本仓库提供 Git 地址安装和手动安装方式，不代表已经收录到 ComfyUI Manager 节点注册表。

## 下载模型

### 必需：Qwen3-VL

Windows 便携版执行：

```bat
python_embeded\python.exe ComfyUI\custom_nodes\ComfyUI-H3-LocalPrompt\download_models.py --comfy-root ComfyUI
```

下载位置：

```text
ComfyUI/models/LLM/Qwen3-VL-4B-Instruct/
```

需要完整的模型目录，包括权重、配置、tokenizer 和 processor 文件。不能只下载一个 `.safetensors` 文件。

原 H3 工作流中的 Qwen CLIP 编码器不能替代这个独立的视频分析模型。

### 可选：Whisper 语音转写

执行：

```bat
python_embeded\python.exe ComfyUI\custom_nodes\ComfyUI-H3-LocalPrompt\download_models.py --comfy-root ComfyUI --audio
```

这个命令会确保 Qwen 模型已下载，并额外下载 Whisper 模型。

Whisper 下载位置：

```text
ComfyUI/models/LLM/faster-whisper-small/
```

首次安装依赖和下载模型需要联网。下载完成后，节点使用本地模型文件推理，无需付费 API。

也可以在另一台电脑下载模型，再复制完整目录。

## 工作流使用

### 先分析、再检查

导入：

```text
workflows/H3_Local_Analyze_Only.json
```

1. 在参考视频节点重新选择本地视频。
2. 确认视频截取范围及有效时长。
3. 在原产品图片节点选择产品参考图。
4. 设置目标视频时长。
5. 运行工作流。
6. 在提示词预览节点查看英文提示词和中文报告。

这个版本禁用了 H3 生成分支，适合首次检查识别结果。

### 自动分析并生成视频

导入：

```text
workflows/H3_Local_Auto.json
```

确认原工作流所需的 H3 模型、LoRA、图片、音频和自定义节点均已安装，然后运行。

流程为：

```text
参考视频 → 本地分析 → 提示词预览/覆盖 → H3 生成
```

**自动版不会在预览节点暂停。** 一次运行会继续生成视频。需要先审核时，请使用仅分析版。

### 手动修改提示词

在 `H3PromptReview` 的 `manual_override` 中粘贴修改后的完整英文提示词：

- 留空：使用自动生成结果。
- 填写内容：使用手动填写的完整提示词。

手动覆盖仍会执行上游视频分析，不会跳过 Qwen 模型加载。

## 分析节点参数

| 参数 | 作用 |
|---|---|
| `model_folder` | Qwen 模型目录名称或绝对路径 |
| `device` | `cpu` 或 `cuda` |
| `max_frames` | 均匀抽取的帧数量 |
| `max_side` | 分析图片的最长边像素数 |
| `max_new_tokens` | 最大输出 token 数 |
| `transcribe` | 是否开启本地台词转写 |
| `whisper_folder` | Whisper 模型目录 |
| `direction` | 创作要求，例如语言、风格、产品约束 |
| `product_image` | 可选产品参考图 |
| `audio` | 开启转写时所需的参考视频音频 |

默认设置：

```text
device: cpu
max_frames: 12
max_side: 448
max_new_tokens: 1400
transcribe: false
```

## 资源需求

### CPU

默认使用 CPU，速度可能较慢。

4B 模型使用 float32 时，仅参数约占 16GB 内存。考虑视觉输入、推理和 ComfyUI 其他内容，建议至少 32GB 系统内存；实际需求可能更高。

### CUDA

需要支持 CUDA 的显卡和可用的 PyTorch CUDA 环境。

bf16/fp16 模型参数约占 8GB 显存，视觉输入和推理缓存还会占用额外显存。12–16GB 显存只是经验起点，不能保证所有设置都能运行。

显存不足可先尝试：

```text
max_frames: 6–8
max_side: 336
```

仍不足时可切换 CPU，并确认系统内存足够。

CUDA 分析前会请求 ComfyUI 卸载已有模型，分析后释放 Qwen；实际显存使用仍受工作流调度影响。本节点没有自动量化或多设备切分。

## 原工作流改动

- 启用原本处于旁路状态的参考视频节点。
- 从缩放前的视频帧分出分析支路。
- 将自动提示词接入 H3 的 `prompt`。
- 将原手写提示词保留为断开的备份。
- 保留原参考视频输入、模型、LoRA、采样参数及输出路线。

工作流中的视频文件名只是原文件引用，不包含实际视频。导入后必须重新选择本地素材。

## 识别范围与限制

- 使用按时间排列的抽帧序列分析，可能漏掉快速动作、短镜头和短暂出现的物体。
- 时间戳以截取片段起点为零，依赖视频节点输出帧与时长保持一致。
- 关闭语音转写时，只分析画面，不识别原视频台词、音乐或环境音。
- Whisper 用于语音转写，不是音乐或音效分类器；转写结果需要人工核对。
- 创作要求和参考视频实际内容可能不同，分析报告会要求模型区分两者。
- 自动提示词不保证 H3 精确执行，也不保证产品结构百分之百复原。
- 本节点不写死未经确认的媒体标签。如果你的 H3 扩展要求特定标签，请在 `direction` 或手动提示词中补充。

## 常见问题

### 找不到新增节点

检查：

1. 文件夹是否放入 `ComfyUI/custom_nodes/`。
2. `__init__.py` 是否直接位于节点文件夹根目录。
3. 依赖是否安装在 ComfyUI 使用的 Python 环境中。
4. 是否完全重启 ComfyUI。
5. 启动日志中是否有该节点的导入错误。

### 找不到 Qwen3VLForConditionalGeneration

当前 Python 环境的 Transformers 必须支持 Qwen3-VL。请检查依赖安装结果，以及其他插件是否存在版本冲突。

### 模型目录缺少 config.json

请下载完整 Hugging Face 模型目录，不能只放权重文件。

### CUDA out of memory

降低抽帧数量和图片尺寸，或改用 CPU。

### 模型返回 JSON 不完整

提高 `max_new_tokens`，或减少抽帧数量、缩短 `direction`。

### 原有工作流节点缺失

本仓库只提供新增的两个节点。原工作流中的 LoadVideoUI、LayerStyle、H3 等扩展仍需自行安装。

## 官方参考

- [Qwen3-VL-4B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [ComfyUI 自定义节点文档](https://docs.comfy.org/custom-nodes/overview)
