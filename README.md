# 小学二年级练习题生成器

这是一个通过大模型来生成小学二年级仿写题和看图写话的生成器，可以自动生成Word文档，并为看图写话题目生成配图。

## 功能特点

- 自动生成句子仿写练习题，包含例句和参考答案
- 自动生成看图写话练习题，并使用AI生成相应的图片
- 将生成的题目和图片整合到一个Word文档中
- 自动保存生成的图片到本地
- 支持自定义题目数量和要求

## 环境要求

- Python 3.11 或更高版本
- 需要有效的大模型API密钥（支持OpenAI兼容接口）
- 需要有效的图像生成API密钥（支持OpenAI兼容接口）

## 安装步骤

1. 克隆或下载本仓库到本地

2. 创建并激活虚拟环境（推荐）
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. 安装依赖包
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 配置参数

在`main.py`文件中，找到`main()`函数，根据需要修改以下参数：

```python
# 模型API配置
api_key = "your-model-api-key"  # 模型API密钥
base_url = "https://api.example.com/v1"  # 模型API基础URL
model_name = "model-name"  # 模型名称
model_type = "openai"  # 模型类型

# 图片生成API配置
image_api_key = "your-image-api-key"  # 图片生成API密钥
image_base_url = "https://api.example.com/v1"  # 图片生成API基础URL
image_model = "dall-e-3"  # 图片生成模型
image_size = "1024x1024"  # 图片尺寸
image_model_type = "openai"  # 图片生成模型类型
image_delay = 2.0  # 图片生成请求之间的延迟时间（秒）

# 题目生成参数
imitation_count = 5  # 句子仿写题数量
picture_count = 2  # 看图写话题数量
user_requirements = "题目难度适合小学二年级学生"  # 用户要求
```

### 参数说明

#### 模型API配置
- `api_key`: 用于访问大模型API的密钥
- `base_url`: 大模型API的基础URL
- `model_name`: 使用的模型名称，如"deepseek-ai/DeepSeek-V3"
- `model_type`: 模型类型，目前支持"openai"

#### 图片生成API配置
- `image_api_key`: 用于访问图片生成API的密钥
- `image_base_url`: 图片生成API的基础URL
- `image_model`: 图片生成模型，如"dall-e-3"
- `image_size`: 生成图片的尺寸，如"1024x1024"
- `image_model_type`: 图片生成模型类型，目前支持"openai"
- `image_delay`: 生成多张图片时，每次请求之间的延迟时间（秒）

#### 题目生成参数
- `imitation_count`: 要生成的句子仿写题数量
- `picture_count`: 要生成的看图写话题数量
- `user_requirements`: 对题目的特殊要求，如难度、主题等

### 运行程序

配置好参数后，直接运行`main.py`文件：

```bash
python main.py
```

## 输出结果

程序运行后，会在`data`目录下创建一个以时间戳命名的文件夹（格式：YYYYMMDD_HHMMSS），其中包含：

- `exercises.json`: 原始题目数据
- `exercises_with_images.json`: 包含图片URL和本地路径的题目数据
- `exercises.docx`: 生成的Word文档，包含所有题目和图片
- 图片文件: 格式为`image_YYYYMMDD_HHMMSS.png`

## 注意事项

1. 请确保提供有效的API密钥，否则程序将无法正常工作
2. 图片生成可能需要较长时间，请耐心等待
3. 如果遇到网络问题，可以适当增加`image_delay`的值
4. 生成的图片和文档会自动保存，无需手动操作
5. 参考答案会自动添加到Word文档的最后一页

## 常见问题

**Q: 为什么图片生成失败？**  
A: 可能是API密钥无效、网络问题或API限制。请检查API密钥并确保网络连接正常。

**Q: 如何修改生成题目的风格？**  
A: 可以通过修改`user_requirements`参数来调整题目风格和内容。

**Q: 可以生成其他类型的题目吗？**  
A: 目前仅支持句子仿写和看图写话两种类型。如需其他类型，需要修改代码。

## 开发者扩展

本项目设计为可扩展的架构，开发者可以根据自己的需求进行以下扩展：

1. **支持更多模型类型**：
   - 在`call_model`函数中添加对其他模型API格式的支持
   - 目前支持OpenAI兼容接口，可以扩展支持其他API格式

2. **支持更多图像生成模型**：
   - 在`generate_image`函数中添加对其他图像生成API的支持
   - 可以实现对Stable Diffusion、Midjourney等其他图像生成服务的调用

3. **添加新的题型**：
   - 修改系统提示词以支持生成新的题型
   - 在`WordGenerator`类中添加对应的处理方法

4. **自定义文档格式**：
   - 修改`WordGenerator`类以支持不同的文档样式和格式
   - 可以扩展支持导出为PDF、HTML等其他格式

开发者可以根据注释和代码结构，轻松地进行功能扩展和定制，无需修改核心逻辑。

## 许可证

[Apache-2.0 license](LICENSE)
