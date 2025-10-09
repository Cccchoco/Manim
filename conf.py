# 导入os模块，用于处理文件路径和操作系统相关功能
import os
# 导入sys模块，用于访问Python解释器的相关变量和功能
import sys

# 将当前目录的绝对路径添加到模块搜索路径的最前面
# 这样Python会优先在当前目录查找导入的模块
sys.path.insert(0, os.path.abspath("."))

# 将当前目录上两级的目录绝对路径添加到模块搜索路径的最前面
# 用于导入位于项目更上层目录中的模块
sys.path.insert(0, os.path.abspath('../../'))


# 项目名称，会显示在文档的标题等位置
project = 'manim'

# 版权信息，这里声明文档已进入公共领域
copyright = '- This document has been placed in the public domain.'

# 文档作者
author = 'TonyCrane'

# 文档版本号，这里为空表示不指定具体版本
release = ''

# 配置Sphinx扩展插件
extensions = [
    'sphinx.ext.todo',           # 支持待办事项(todo)标记
    'sphinx.ext.githubpages',    # 简化GitHub Pages部署
    'sphinx.ext.mathjax',        # 支持MathJax渲染数学公式
    'sphinx.ext.intersphinx',    # 支持跨文档引用
    'sphinx.ext.autodoc',        # 自动从Python代码生成文档
    'sphinx.ext.coverage',       # 检查文档覆盖率
    'sphinx.ext.napoleon',       # 支持NumPy和Google风格的文档字符串
    'sphinx_copybutton',         # 为代码块添加复制按钮
    'manim_example_ext'          # Manim专用的示例扩展（可能用于渲染动画示例）
]

# 配置autodoc扩展：文档中同时包含类的文档字符串和构造函数文档
autoclass_content = 'both'

# 配置MathJax的加载路径，使用CDN加速
mathjax_path = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"

# 模板文件存放路径
templates_path = ['_templates']

# 源文件的后缀名，这里使用reStructuredText格式
source_suffix = '.rst'

# 文档的主入口文件（首页）
master_doc = 'index'

# 代码高亮风格，使用默认风格
pygments_style = 'default'

# 静态文件（CSS、JS、图片等）的存放路径
html_static_path = ["_static"]

# 额外加载的CSS文件，使用CDN加速
html_css_files = [
    "https://cdn.jsdelivr.net/gh/manim-kindergarten/CDN@master/manimgl_assets/custom.css", 
    "https://cdn.jsdelivr.net/gh/manim-kindergarten/CDN@master/manimgl_assets/colors.css"
]

# 配置HTML主题为furo（现代风格的文档主题）
html_theme = 'furo'  # 提示需要安装特定版本：pip install furo==2020.10.5b9

# 网站图标
html_favicon = '_static/icon.png'

# 网站Logo
html_logo = '../../logo/transparent_graph.png'

# 配置HTML主题的额外选项
html_theme_options = {
    "sidebar_hide_name": True,  # 在侧边栏隐藏项目名称
}
