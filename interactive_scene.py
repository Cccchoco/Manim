from __future__ import annotations

# 导入itertools模块并简写为it，该模块提供了用于创建高效迭代器的函数
# 常用于循环操作、组合生成、排列生成等场景
import itertools as it

# 导入numpy库并简写为np，这是Python中用于科学计算的核心库
# 提供了高性能的多维数组对象和数学函数，广泛用于数据分析、矩阵运算等
import numpy as np

# 导入pyperclip模块，该模块提供了跨平台的剪贴板访问功能
# 可以实现文本的复制到剪贴板和从剪贴板粘贴操作
import pyperclip

# 从IPython.core.getipython模块导入get_ipython函数
# 该函数用于获取当前IPython解释器实例，常用于IPython环境下的交互操作
from IPython.core.getipython import get_ipython

# 从pyglet.window.key模块导入key并简写为PygletWindowKeys
# pyglet是一个用于多媒体应用开发的库，这里导入的是键盘事件相关的常量
# 常用于处理游戏或交互应用中的键盘输入
from pyglet.window import key as PygletWindowKeys

# 从manimlib的淡入动画模块导入FadeIn类
# 该类用于创建元素淡入的动画效果
from manimlib.animation.fading import FadeIn

# 从manimlib配置模块导入manim_config对象
# 存储Manim的配置信息，可访问和修改渲染参数等设置
from manimlib.config import manim_config

# 从manimlib常量模块导入方向常量
# 分别表示左下、下、右下、左、原点、右、左上、上、右上方向
from manimlib.constants import DL, DOWN, DR, LEFT, ORIGIN, RIGHT, UL, UP, UR

# 从manimlib常量模块导入屏幕尺寸和间距常量
# FRAME_WIDTH/FRAME_HEIGHT表示场景的宽高，SMALL_BUFF表示小间距值
from manimlib.constants import FRAME_WIDTH, FRAME_HEIGHT, SMALL_BUFF

# 导入圆周率常量π，用于角度和几何计算
from manimlib.constants import PI

# 导入角度单位常量DEG（度），用于角度相关计算
from manimlib.constants import DEG

# 导入颜色相关常量
# MANIM_COLORS是颜色字典，WHITE是白色，GREY_A和GREY_C是不同深度的灰色
from manimlib.constants import MANIM_COLORS, WHITE, GREY_A, GREY_C

# 从几何模块导入基本几何图形类
# Line（线段）、Rectangle（矩形）、Square（正方形）
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import Square

# 从mobject模块导入组合对象类
# Group（普通组合对象）、Mobject（所有可渲染对象的基类）
from manimlib.mobject.mobject import Group
from manimlib.mobject.mobject import Mobject

# 从数字模块导入DecimalNumber类，用于显示带小数的数字
from manimlib.mobject.numbers import DecimalNumber

# 从SVG模块导入文本相关类
# Tex用于显示LaTeX公式，Text用于显示普通文本
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.text_mobject import Text

# 从点云类型模块导入DotCloud类，用于创建点云对象
from manimlib.mobject.types.dot_cloud import DotCloud

# 从向量化对象类型模块导入相关类
# VGroup（向量化组合对象）、VHighlight（向量化高亮对象）、VMobject（向量化可渲染对象基类）
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VHighlight
from manimlib.mobject.types.vectorized_mobject import VMobject

# 从场景模块导入场景相关类
# Scene是所有动画场景的基类，SceneState用于管理场景状态
from manimlib.scene.scene import Scene
from manimlib.scene.scene import SceneState

# 从家族操作工具模块导入提取对象家族成员的函数
# 用于获取一个对象及其所有子对象的集合
from manimlib.utils.family_ops import extract_mobject_family_members

# 从空间操作工具模块导入求范数的函数，用于计算向量的长度
from manimlib.utils.space_ops import get_norm

# 从LaTeX文件写入工具模块导入LaTeX错误类
# 用于处理LaTeX公式生成过程中的错误
from manimlib.utils.tex_file_writing import LatexError

# 从typing模块导入TYPE_CHECKING常量，用于类型检查时的条件导入
from typing import TYPE_CHECKING

# 当进行类型检查时（非运行时），导入Vect3类型用于类型注解
if TYPE_CHECKING:
    from manimlib.typing import Vect3


# 从manim配置中获取各种操作的按键绑定
# 选择功能的按键
SELECT_KEY = manim_config.key_bindings.select
# 取消选择功能的按键
UNSELECT_KEY = manim_config.key_bindings.unselect
# 抓取（移动）功能的按键
GRAB_KEY = manim_config.key_bindings.grab
# 沿X轴抓取（移动）的按键
X_GRAB_KEY = manim_config.key_bindings.x_grab
# 沿Y轴抓取（移动）的按键
Y_GRAB_KEY = manim_config.key_bindings.y_grab
# 所有与抓取相关的按键列表
GRAB_KEYS = [GRAB_KEY, X_GRAB_KEY, Y_GRAB_KEY]
# 调整大小功能的按键（待实现）
RESIZE_KEY = manim_config.key_bindings.resize  # TODO
# 颜色调整功能的按键
COLOR_KEY = manim_config.key_bindings.color
# 信息显示功能的按键
INFORMATION_KEY = manim_config.key_bindings.information
# 光标功能的按键
CURSOR_KEY = manim_config.key_bindings.cursor

# 用于键盘交互的配置

# 方向键符号的ASCII码列表（左、上、右、下）
ARROW_SYMBOLS: list[int] = [
    PygletWindowKeys.LEFT,
    PygletWindowKeys.UP,
    PygletWindowKeys.RIGHT,
    PygletWindowKeys.DOWN,
]

# 所有修饰键（Ctrl、Command、Shift）的组合掩码
ALL_MODIFIERS = PygletWindowKeys.MOD_CTRL | PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_SHIFT

# 注意：这里的许多功能仍有bug，且大多处于开发中


class InteractiveScene(Scene):
    """
    交互场景类，继承自基础场景类Scene
    
    使用说明：
    - 要选择屏幕上的物体，按住Ctrl键并移动鼠标来框选区域，
      或直接点击Ctrl键选择光标下的物体
    - 按Command + t可切换选择模式：选择场景中的顶级物体或底层组件
    - 按住'g'键可抓取选中的物体并移动
    - 按住'h'键可沿水平方向拖动选中物体
    - 按住'v'键可沿垂直方向拖动选中物体
    - 按住't'键可调整选中物体大小，配合Shift键可相对于角落调整大小
    - Command + 'c'将选中物体的ID复制到剪贴板
    - Command + 'v'可粘贴内容：
        - 复制的物体
        - 基于复制的LaTeX生成的Tex物体
        - 基于复制的文本生成的Text物体
    - Command + 'z'将选中物体恢复到原始状态
    - Command + 's'将选中的物体保存到文件
    """
    # 选中物体角落点的配置字典
    corner_dot_config = dict(
        color=WHITE,          # 颜色为白色
        radius=0.05,          # 半径为0.05
        glow_factor=2.0,      # 发光系数为2.0
    )
    # 选择矩形的边框颜色
    selection_rectangle_stroke_color = WHITE
    # 选择矩形的边框宽度
    selection_rectangle_stroke_width = 1.0
    # 调色板颜色，使用MANIM默认颜色集
    palette_colors = MANIM_COLORS
    # 选中物体的微调大小
    selection_nudge_size = 0.05
    # 光标位置显示的配置
    cursor_location_config = dict(
        font_size=24,         # 字体大小24
        fill_color=GREY_C,    # 填充色为灰色C
        num_decimal_places=3, # 保留3位小数
    )
    # 时间标签的配置
    time_label_config = dict(
        font_size=24,         # 字体大小24
        fill_color=GREY_C,    # 填充色为灰色C
        num_decimal_places=1, # 保留1位小数
    )
    # 十字准星的宽度
    crosshair_width = 0.2
    # 十字准星的样式配置
    crosshair_style = dict(
        stroke_color=GREY_A,  # 边框颜色为灰色A
        stroke_width=[3, 0, 3], # 边框宽度（三个值分别对应不同部分）
    )

def setup(self):
    # 创建一个组用于存储选中的对象
    self.selection = Group()
    # 获取选中对象的高亮显示效果
    self.selection_highlight = self.get_selection_highlight()
    # 获取选择矩形框（用于框选操作）
    self.selection_rectangle = self.get_selection_rectangle()
    # 获取十字光标
    self.crosshair = self.get_crosshair()
    # 获取信息标签（显示坐标和时间等信息）
    self.information_label = self.get_information_label()
    # 获取颜色选择面板
    self.color_palette = self.get_color_palette()
    # 定义不可选中的对象列表
    self.unselectables = [
        self.selection,               # 选中对象组本身不可再被选中
        self.selection_highlight,     # 高亮显示效果不可被选中
        self.selection_rectangle,     # 选择矩形框不可被选中
        self.crosshair,               # 十字光标不可被选中
        self.information_label,       # 信息标签不可被选中
        self.camera.frame             # 相机框架不可被选中
    ]
    # 设置是否只选中顶层的可移动对象
    self.select_top_level_mobs = True
    # 重新生成用于选择操作的搜索集合
    self.regenerate_selection_search_set()

    # 初始化选择状态：未处于选择状态
    self.is_selecting = False
    # 初始化拖拽状态：未处于拖拽状态
    self.is_grabbing = False

    # 将选中对象的高亮显示效果添加到场景中
    self.add(self.selection_highlight)

def get_selection_rectangle(self):
    # 创建一个矩形框，用于框选操作
    rect = Rectangle(
        stroke_color=self.selection_rectangle_stroke_color,  # 设置边框颜色
        stroke_width=self.selection_rectangle_stroke_width,  # 设置边框宽度
    )
    # 固定矩形框在框架中，不随相机移动
    rect.fix_in_frame()
    # 设置矩形框的固定角为原点（通常是左上角）
    rect.fixed_corner = ORIGIN
    # 为矩形框添加更新器，当状态变化时更新显示
    rect.add_updater(self.update_selection_rectangle)
    return rect

def update_selection_rectangle(self, rect: Rectangle):
    # 获取矩形框的起始点（固定角）
    p1 = rect.fixed_corner
    # 将鼠标当前位置转换为固定框架中的坐标点
    p2 = self.frame.to_fixed_frame_point(self.mouse_point.get_center())
    # 根据起始点和鼠标位置设置矩形框的四个角点，形成矩形
    rect.set_points_as_corners([
        p1, np.array([p2[0], p1[1], 0]),  # 右上角点
        p2, np.array([p1[0], p2[1], 0]),  # 左下角点
        p1,                               # 回到起始点，闭合矩形
    ])
    return rect

def get_selection_highlight(self):
    # 创建一个组用于显示选中对象的高亮效果
    result = Group()
    # 存储被跟踪的（即被选中的）可移动对象
    result.tracked_mobjects = []
    # 为高亮效果添加更新器，当选中对象变化时更新显示
    result.add_updater(self.update_selection_highlight)
    return result

def update_selection_highlight(self, highlight: Mobject):
    # 如果当前跟踪的对象与选中的对象相同，则不需要更新
    if set(highlight.tracked_mobjects) == set(self.selection):
        return

    # 否则，刷新高亮效果的内容
    highlight.tracked_mobjects = list(self.selection)
    # 为每个选中的对象创建高亮显示，并设置为高亮组的子对象
    highlight.set_submobjects([
        self.get_highlight(mob) for mob in self.selection
    ])
    try:
        # 找到选中对象在场景对象列表中的最小索引位置
        index = min((
            i for i, mob in enumerate(self.mobjects)
            for sm in self.selection
            if sm in mob.get_family()
        ))
        # 将高亮效果从场景中移除后重新插入到合适位置（选中对象下方）
        self.mobjects.remove(highlight)
        self.mobjects.insert(index - 1, highlight)
    except ValueError:
        # 如果找不到索引（如无选中对象），则不做处理
        pass

def get_crosshair(self):
    # 创建一个向量对象并复制一份，用于组成十字光标
    lines = VMobject().replicate(2)
    # 设置第一条线为水平线（从左到右穿过原点）
    lines[0].set_points([LEFT, ORIGIN, RIGHT])
    # 设置第二条线为垂直线（从上到下穿过原点）
    lines[1].set_points([UP, ORIGIN, DOWN])
    # 将两条线组合成十字光标
    crosshair = VGroup(*lines)

    # 设置十字光标的宽度
    crosshair.set_width(self.crosshair_width)
    # 应用十字光标的样式（颜色、线宽等）
    crosshair.set_style(** self.crosshair_style)
    # 设置十字光标为动画状态
    crosshair.set_animating_status(True)
    # 固定十字光标在框架中，随鼠标移动
    crosshair.fix_in_frame()
    return crosshair

def get_color_palette(self):
    # 创建一个颜色选择面板，由多个填充了不同颜色的正方形组成
    palette = VGroup(*(
        Square(fill_color=color, fill_opacity=1, side_length=1)
        for color in self.palette_colors  # 从预设的调色板颜色列表中获取颜色
    ))
    # 去除正方形的边框
    palette.set_stroke(width=0)
    # 水平排列颜色方块，设置间距
    palette.arrange(RIGHT, buff=0.5)
    # 设置面板宽度为框架宽度减去0.5的边距
    palette.set_width(FRAME_WIDTH - 0.5)
    # 将面板放置在底部边缘，设置小间距
    palette.to_edge(DOWN, buff=SMALL_BUFF)
    # 固定面板在框架中，不随相机移动
    palette.fix_in_frame()
    return palette

def get_information_label(self):
    # 创建一个向量组，包含三个十进制数字显示框，用于显示坐标
    loc_label = VGroup(*(
        DecimalNumber(**self.cursor_location_config)  # 应用坐标显示的配置
        for n in range(3)  # 三个坐标值：x, y, z
    ))

    # 定义坐标标签的更新函数
    def update_coords(loc_label):
        # 遍历坐标标签和鼠标位置的三个坐标值
        for mob, coord in zip(loc_label, self.mouse_point.get_location()):
            # 更新数字显示框的值为当前坐标
            mob.set_value(coord)
        # 水平排列坐标标签，间距为标签高度
        loc_label.arrange(RIGHT, buff=loc_label.get_height())
        # 将坐标标签放置在右下角，设置小间距
        loc_label.to_corner(DR, buff=SMALL_BUFF)
        # 固定坐标标签在框架中
        loc_label.fix_in_frame()
        return loc_label

    # 为坐标标签添加更新器，实时更新显示
    loc_label.add_updater(update_coords)

    # 创建一个十进制数字显示框，用于显示时间
    time_label = DecimalNumber(0,** self.time_label_config)  # 应用时间显示的配置
    # 将时间标签放置在左下角，设置小间距
    time_label.to_corner(DL, buff=SMALL_BUFF)
    # 固定时间标签在框架中
    time_label.fix_in_frame()
    # 为时间标签添加更新器，每帧增加流逝的时间
    time_label.add_updater(lambda m, dt: m.increment_value(dt))

    # 将坐标标签和时间标签组合成一个信息标签组并返回
    return VGroup(loc_label, time_label)

    # 重写方法
def get_state(self):
    # 返回场景状态，忽略指定的交互元素（不保存它们的状态）
    return SceneState(self, ignore=[
        self.selection_highlight,  # 忽略选中高亮效果
        self.selection_rectangle,  # 忽略选择矩形框
        self.crosshair,            # 忽略十字光标
    ])

def restore_state(self, scene_state: SceneState):
    # 调用父类方法恢复场景状态
    super().restore_state(scene_state)
    # 将选中高亮效果插入到场景对象列表的最前面（确保显示在最底层）
    self.mobjects.insert(0, self.selection_highlight)

def add(self, *mobjects: Mobject):
    # 调用父类方法添加对象到场景
    super().add(*mobjects)
    # 重新生成选择搜索集合（因为场景中的对象发生了变化）
    self.regenerate_selection_search_set()

def remove(self, *mobjects: Mobject):
    # 调用父类方法从场景中移除对象
    super().remove(*mobjects)
    # 重新生成选择搜索集合（因为场景中的对象发生了变化）
    self.regenerate_selection_search_set()

def remove_all_except(self, *mobjects_to_keep : Mobject):
    # 调用父类方法移除除指定对象外的所有对象
    super().remove_all_except(*mobjects_to_keep)
    # 重新生成选择搜索集合（因为场景中的对象发生了变化）
    self.regenerate_selection_search_set()

# 与选择相关的方法

def toggle_selection_mode(self):
    # 切换选择模式（顶层对象/所有子对象）
    self.select_top_level_mobs = not self.select_top_level_mobs
    # 刷新选择范围（根据新模式调整当前选择）
    self.refresh_selection_scope()
    # 重新生成选择搜索集合（根据新模式更新可选择对象）
    self.regenerate_selection_search_set()

def get_selection_search_set(self) -> list[Mobject]:
    # 返回当前可用于选择的对象集合
    return self.selection_search_set

def regenerate_selection_search_set(self):
    # 过滤出所有不在不可选中列表中的对象，作为可选择对象的基础
    selectable = list(filter(
        lambda m: m not in self.unselectables,
        self.mobjects
    ))
    # 根据选择模式确定可选择对象集合
    if self.select_top_level_mobs:
        # 顶层模式：仅顶层对象可被选择
        self.selection_search_set = selectable
    else:
        # 子对象模式：所有子对象（带有点信息的）都可被选择
        self.selection_search_set = [
            submob
            for mob in selectable
            for submob in mob.family_members_with_points()  # 获取所有带点的子对象
        ]

def refresh_selection_scope(self):
    # 保存当前选中的对象
    curr = list(self.selection)
    # 根据选择模式调整选中的对象范围
    if self.select_top_level_mobs:
        # 顶层模式：选中包含当前选中子对象的所有顶层对象
        self.selection.set_submobjects([
            mob
            for mob in self.mobjects
            if any(sm in mob.get_family() for sm in curr)  # 检查是否包含当前选中的子对象
        ])
        # 刷新选中对象组的边界框（递归向下检查）
        self.selection.refresh_bounding_box(recurse_down=True)
    else:
        # 子对象模式：从当前选中对象中提取所有子对象（排除无意义的点）
        self.selection.set_submobjects(
            extract_mobject_family_members(
                curr, exclude_pointless=True,  # 排除无意义的子对象
            )
        )

def get_corner_dots(self, mobject: Mobject) -> Mobject:
    # 创建用于标记对象角落的点云（根据配置）
    dots = DotCloud(** self.corner_dot_config)
    # 从配置中获取点的半径
    radius = float(self.corner_dot_config["radius"])
    # 根据对象的深度判断是2D还是3D对象
    if mobject.get_depth() < 1e-2:  # 近似为2D对象
        # 2D对象使用四个角落方向（左下、左上、右上、右下）
        vects = [DL, UL, UR, DR]
    else:  # 3D对象
        # 3D对象使用8个角落方向（x,y,z轴的正负组合）
        vects = np.array(list(it.product(*3 * [[-1, 1]])))
    # 为点云添加更新器，使其始终位于对象的角落
    dots.add_updater(lambda d: d.set_points([
        mobject.get_corner(v) + v * radius  # 角落位置向外偏移一个半径
        for v in vects
    ]))
    return dots

def get_highlight(self, mobject: Mobject) -> Mobject:
    # 根据对象类型返回不同的高亮效果
    # 如果是带有点的向量对象且处于子对象选择模式
    if isinstance(mobject, VMobject) and mobject.has_points() and not self.select_top_level_mobs:
        # 计算对象的最大尺寸（高度或宽度）
        length = max([mobject.get_height(), mobject.get_width()])
        # 创建向量高亮效果，根据对象尺寸调整高亮强度
        result = VHighlight(
            mobject,
            max_stroke_addition=min([50 * length, 10]),  # 高亮强度限制在10以内
        )
        # 添加更新器，使高亮效果跟随对象变化（拉伸适应）
        result.add_updater(lambda m: m.replace(mobject, stretch=True))
        return result
    # 如果是点云对象，则返回空对象（不显示高亮）
    elif isinstance(mobject, DotCloud):
        return Mobject()
    # 其他类型的对象使用角落点作为高亮
    else:
        return self.get_corner_dots(mobject)

def add_to_selection(self, *mobjects: Mobject):
    # 过滤出不在不可选中列表且未被选中的对象
    mobs = list(filter(
        lambda m: m not in self.unselectables and m not in self.selection,
        mobjects
    ))
    # 如果没有符合条件的对象，则直接返回
    if len(mobs) == 0:
        return
    # 将过滤后的对象添加到选中集合
    self.selection.add(*mobs)
    # 为每个新选中的对象设置动画状态（可能用于高亮动画）
    for mob in mobs:
        mob.set_animating_status(True)

def toggle_from_selection(self, *mobjects: Mobject):
    # 切换对象的选中状态（选中→取消，未选中→选中）
    for mob in mobjects:
        if mob in self.selection:
            # 如果对象已选中，则从选中集合中移除
            self.selection.remove(mob)
            # 取消动画状态
            mob.set_animating_status(False)
            # 刷新对象的边界框
            mob.refresh_bounding_box()
        else:
            # 如果对象未选中，则添加到选中集合
            self.add_to_selection(mob)

def clear_selection(self):
    # 清除所有选中对象
    for mob in self.selection:
        # 取消每个对象的动画状态
        mob.set_animating_status(False)
        # 刷新对象的边界框
        mob.refresh_bounding_box()
    # 清空选中集合
    self.selection.set_submobjects([])

def disable_interaction(self, *mobjects: Mobject):
    # 禁用指定对象的交互（使其不可被选中）
    for mob in mobjects:
        # 将对象及其所有子对象添加到不可选中列表
        for sm in mob.get_family():
            self.unselectables.append(sm)
    # 重新生成选择搜索集合（因为可选择对象发生了变化）
    self.regenerate_selection_search_set()

def enable_interaction(self, *mobjects: Mobject):
    # 启用指定对象的交互（使其可被选中）
    for mob in mobjects:
        # 将对象及其所有子对象从不可选中列表中移除
        for sm in mob.get_family():
            if sm in self.unselectables:
                self.unselectables.remove(sm)
    # 重新生成选择搜索集合（因为可选择对象发生了变化）
    self.regenerate_selection_search_set()
    # Functions for keyboard actions

def copy_selection(self):
    # 存储选中对象的名称列表
    names = []
    # 获取当前的IPython shell（用于查找对象的变量名）
    shell = get_ipython()
    # 遍历每个选中的对象
    for mob in self.selection:
        # 默认使用对象的ID作为名称
        name = str(id(mob))
        # 如果IPython shell存在（即在Jupyter环境中）
        if shell is None:
            continue
        # 遍历用户命名空间中的变量，查找引用该对象的变量名
        for key, value in shell.user_ns.items():
            if mob is value:
                name = key  # 找到后使用变量名作为名称
        # 将找到的名称添加到列表
        names.append(name)
    # 将名称列表用逗号分隔后复制到剪贴板
    pyperclip.copy(", ".join(names))

def paste_selection(self):
    # 从剪贴板获取内容
    clipboard_str = pyperclip.paste()
    # 尝试粘贴为图形对象（Mobject）
    try:
        # 将剪贴板内容按逗号分割并转换为整数（假设是对象ID）
        ids = map(int, clipboard_str.split(","))
        # 根据ID查找对应的对象
        mobs = map(self.id_to_mobject, ids)
        # 复制找到的对象（过滤掉None）
        mob_copies = [m.copy() for m in mobs if m is not None]
        # 清除当前选中状态
        self.clear_selection()
        # 播放淡入动画，新复制的对象从1.5倍缩放状态淡入
        self.play(*(
            FadeIn(mc, run_time=0.5, scale=1.5)
            for mc in mob_copies
        ))
        # 将新复制的对象添加到选中状态
        self.add_to_selection(*mob_copies)
        return  # 成功粘贴对象后返回
    except ValueError:
        pass  # 如果无法解析为ID，则继续尝试其他格式
    # 否则，将剪贴板内容视为Tex或普通文本
    # 检查是否包含LaTeX相关符号（作为判断是否为LaTeX的简单方法）
    if set("\\^=+").intersection(clipboard_str):
        try:
            # 尝试创建LaTeX对象
            new_mob = Tex(clipboard_str)
        except LatexError:
            return  # LaTeX解析失败则返回
    else:
        # 创建普通文本对象
        new_mob = Text(clipboard_str)
    # 清除当前选中状态
    self.clear_selection()
    # 将新创建的文本对象添加到场景
    self.add(new_mob)
    # 将新对象设为选中状态
    self.add_to_selection(new_mob)

def delete_selection(self):
    # 从场景中移除所有选中的对象
    self.remove(*self.selection)
    # 清除选中状态
    self.clear_selection()

def enable_selection(self):
    # 开启选择模式
    self.is_selecting = True
    # 将选择矩形框添加到场景
    self.add(self.selection_rectangle)
    # 设置选择矩形框的起始点为当前鼠标位置（转换为固定框架坐标）
    self.selection_rectangle.fixed_corner = self.frame.to_fixed_frame_point(
        self.mouse_point.get_center()
    )

def gather_new_selection(self):
    # 关闭选择模式
    self.is_selecting = False
    # 如果选择矩形框在场景中
    if self.selection_rectangle in self.mobjects:
        # 从场景中移除选择矩形框
        self.remove(self.selection_rectangle)
        # 存储要添加到选中状态的对象
        additions = []
        # 反向遍历可选择对象集合（确保先选中顶层对象）
        for mob in reversed(self.get_selection_search_set()):
            # 检查对象是否与选择矩形框接触
            if self.selection_rectangle.is_touching(mob):
                additions.append(mob)
                # 如果选择矩形框几乎没有长度（近似为点选），只选一个对象
                if self.selection_rectangle.get_arc_length() < 1e-2:
                    break
        # 切换这些对象的选中状态（选中→取消，未选中→选中）
        self.toggle_from_selection(*additions)

def prepare_grab(self):
    # 获取当前鼠标位置
    mp = self.mouse_point.get_center()
    # 计算鼠标到选中对象中心的偏移量（用于拖拽时保持相对位置）
    self.mouse_to_selection = mp - self.selection.get_center()
    # 开启拖拽模式
    self.is_grabbing = True

def prepare_resizing(self, about_corner=False):
    # 获取选中对象的中心位置
    center = self.selection.get_center()
    # 获取当前鼠标位置
    mp = self.mouse_point.get_center()
    if about_corner:
        # 如果围绕角落缩放，计算缩放参考点（选中对象的角落）
        self.scale_about_point = self.selection.get_corner(center - mp)
    else:
        # 否则围绕中心缩放
        self.scale_about_point = center
    # 计算鼠标到缩放参考点的向量（用于计算缩放比例）
    self.scale_ref_vect = mp - self.scale_about_point
    # 记录当前选中对象的宽度和高度（作为缩放参考）
    self.scale_ref_width = self.selection.get_width()
    self.scale_ref_height = self.selection.get_height()

def toggle_color_palette(self):
    # 如果没有选中对象，则不执行任何操作
    if len(self.selection) == 0:
        return
    # 如果颜色面板不在场景中
    if self.color_palette not in self.mobjects:
        # 保存当前状态
        self.save_state()
        # 添加颜色面板到场景
        self.add(self.color_palette)
    else:
        # 否则从场景中移除颜色面板
        self.remove(self.color_palette)

def display_information(self, show=True):
    if show:
        # 显示信息标签（坐标和时间）
        self.add(self.information_label)
    else:
        # 隐藏信息标签
        self.remove(self.information_label)

def group_selection(self):
    # 将当前选中的所有对象组合成一个组
    group = self.get_group(*self.selection)
    # 将组添加到场景
    self.add(group)
    # 清除当前选中状态
    self.clear_selection()
    # 将新创建的组设为选中状态
    self.add_to_selection(group)

def ungroup_selection(self):
    # 存储解组后的所有子对象
    pieces = []
    # 遍历当前选中的每个对象（通常是一个组）
    for mob in list(self.selection):
        # 从场景中移除该对象
        self.remove(mob)
        # 将对象的所有子对象添加到列表
        pieces.extend(list(mob))
    # 清除当前选中状态
    self.clear_selection()
    # 将解组后的子对象添加到场景
    self.add(*pieces)
    # 将这些子对象设为选中状态
    self.add_to_selection(*pieces)

def nudge_selection(self, vect: np.ndarray, large: bool = False):
    # 获取基础移动距离
    nudge = self.selection_nudge_size
    if large:
        # 如果是大幅度移动，距离乘以10
        nudge *= 10
    # 按照指定方向和距离移动选中的对象
    self.selection.shift(nudge * vect)

    # 键盘操作相关方法
def on_key_press(self, symbol: int, modifiers: int) -> None:
    # 调用父类的键盘按下处理方法（确保基础功能正常）
    super().on_key_press(symbol, modifiers)
    # 将键盘按键编码转换为对应的字符（如按键1的symbol转换为'1'）
    char = chr(symbol)
    
    # 1. 处理选择模式激活：按下"选择键"（SELECT_KEY，需提前定义）且无任何修饰键（Ctrl/Shift等）
    if char == SELECT_KEY and (modifiers & ALL_MODIFIERS) == 0:
        self.enable_selection()
    
    # 2. 处理取消选择：按下"取消选择键"（UNSELECT_KEY，需提前定义）
    if char == UNSELECT_KEY:
        self.clear_selection()
    
    # 3. 处理拖拽准备：按下"拖拽键"（GRAB_KEYS，需提前定义为键列表）且无任何修饰键
    elif char in GRAB_KEYS and (modifiers & ALL_MODIFIERS) == 0:
        self.prepare_grab()
    
    # 4. 处理缩放准备：按下"缩放键"（RESIZE_KEY，需提前定义）且按住Shift修饰键
    elif char == RESIZE_KEY and (modifiers & PygletWindowKeys.MOD_SHIFT):
        # 缩放参考点：根据是否按住Shift决定（此处条件判断冗余，因外层已判断Shift，实际始终为True）
        self.prepare_resizing(about_corner=((modifiers & PygletWindowKeys.MOD_SHIFT) > 0))
    
    # 5. 处理Shift+T组合的缩放准备：按住Shift且按下T键
    elif symbol == PygletWindowKeys.LSHIFT:
        if self.window.is_key_pressed(ord("t")):
            # 围绕角落进行缩放
            self.prepare_resizing(about_corner=True)
    
    # 6. 处理颜色面板切换：按下"颜色键"（COLOR_KEY，需提前定义）且无任何修饰键
    elif char == COLOR_KEY and (modifiers & ALL_MODIFIERS) == 0:
        self.toggle_color_palette()
    
    # 7. 处理信息标签显示：按下"信息键"（INFORMATION_KEY，需提前定义）且无任何修饰键
    elif char == INFORMATION_KEY and (modifiers & ALL_MODIFIERS) == 0:
        self.display_information()
    
    # 8. 处理复制操作：Ctrl+C（Windows/Linux）或Command+C（Mac）
    elif char == "c" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
        self.copy_selection()
    
    # 9. 处理粘贴操作：Ctrl+V（Windows/Linux）或Command+V（Mac）
    elif char == "v" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
        self.paste_selection()
    
    # 10. 处理剪切操作：Ctrl+X（Windows/Linux）或Command+X（Mac）
    elif char == "x" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
        self.copy_selection()  # 先复制选中对象
        self.delete_selection()  # 再删除原选中对象
    
    # 11. 处理删除操作：按下Backspace键
    elif symbol == PygletWindowKeys.BACKSPACE:
        self.delete_selection()
    
    # 12. 处理全选操作：Ctrl+A（Windows/Linux）或Command+A（Mac）
    elif char == "a" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
        self.clear_selection()  # 先清空现有选择
        self.add_to_selection(*self.mobjects)  # 再选中场景中所有对象
    
    # 13. 处理组合操作：Ctrl+G（Windows/Linux）或Command+G（Mac）
    elif char == "g" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
        self.group_selection()  # 将选中对象组合成一个组
    
    # 14. 处理解组操作：Ctrl+Shift+G（Windows/Linux）或Command+Shift+G（Mac）
    elif char == "g" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL | PygletWindowKeys.MOD_SHIFT)):
        self.ungroup_selection()  # 将选中的组解组为单个对象
    
    # 15. 处理选择模式切换：Ctrl+T（Windows/Linux）或Command+T（Mac）
    elif char == "t" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
        self.toggle_selection_mode()  # 切换"仅选顶层对象"/"可选子对象"模式
    
    # 16. 处理帧定位复制：Shift+D（需提前实现copy_frame_positioning方法）
    elif char == "d" and (modifiers & PygletWindowKeys.MOD_SHIFT):
        self.copy_frame_positioning()
    
    # 17. 处理光标位置复制：Shift+C（需提前实现copy_cursor_position方法）
    elif char == "c" and (modifiers & PygletWindowKeys.MOD_SHIFT):
        self.copy_cursor_position()
    
    # 18. 处理方向键微调：按下方向键（ARROW_SYMBOLS需提前定义为方向键symbol列表）
    elif symbol in ARROW_SYMBOLS:
        # 映射方向键到向量：LEFT→左向量，UP→上向量，RIGHT→右向量，DOWN→下向量
        vect = [LEFT, UP, RIGHT, DOWN][ARROW_SYMBOLS.index(symbol)]
        # 按住Shift时为"大幅度微调"，否则为"小幅度微调"
        self.nudge_selection(
            vect=vect,
            large=(modifiers & PygletWindowKeys.MOD_SHIFT),
        )
    
    # 19. 处理十字光标显示/隐藏：按下"光标键"（CURSOR_KEY，需提前定义）
    if char == CURSOR_KEY:
        if self.crosshair in self.mobjects:  # 如果十字光标已在场景中
            self.remove(self.crosshair)  # 隐藏十字光标
        else:  # 如果十字光标不在场景中
            self.add(self.crosshair)  # 显示十字光标
    
    # 20. 选择模式下强制显示十字光标：按下"选择键"时
    if char == SELECT_KEY:
        self.add(self.crosshair)
    
    # 21. 处理状态保存：按下拖拽/缩放相关键时，保存当前场景状态（用于撤销等）
    if char in [GRAB_KEY, X_GRAB_KEY, Y_GRAB_KEY, RESIZE_KEY]:
        self.save_state()


def on_key_release(self, symbol: int, modifiers: int) -> None:
    # 调用父类的键盘释放处理方法（确保基础功能正常）
    super().on_key_release(symbol, modifiers)
    # 将键盘按键编码转换为对应的字符
    char = chr(symbol)
    
    # 1. 处理选择结束：释放"选择键"时，收集框选范围内的对象
    if char == SELECT_KEY:
        self.gather_new_selection()
    
    # 2. 处理拖拽结束：释放"拖拽键"时，关闭拖拽模式
    if char in GRAB_KEYS:
        self.is_grabbing = False
    
    # 3. 处理信息标签隐藏：释放"信息键"时，隐藏信息标签
    elif char == INFORMATION_KEY:
        self.display_information(False)
    
    # 4. 处理Shift+缩放键的释放：释放Shift且仍按住缩放键时，切换为"围绕中心缩放"
    elif symbol == PygletWindowKeys.LSHIFT and self.window.is_key_pressed(ord(RESIZE_KEY)):
        self.prepare_resizing(about_corner=False)


# 鼠标操作相关方法
def handle_grabbing(self, point: Vect3):
    # 计算目标位置：鼠标当前位置减去"鼠标到选中对象中心的偏移量"（保持拖拽时相对位置不变）
    diff = point - self.mouse_to_selection
    
    # 1. 普通拖拽：按住"拖拽键"（GRAB_KEY，需提前定义）时，整体移动选中对象
    if self.window.is_key_pressed(ord(GRAB_KEY)):
        self.selection.move_to(diff)
    
    # 2. X轴拖拽：按住"X轴拖拽键"（X_GRAB_KEY，需提前定义）时，仅沿X轴移动选中对象
    elif self.window.is_key_pressed(ord(X_GRAB_KEY)):
        self.selection.set_x(diff[0])  # 只修改X坐标，Y/Z坐标保持不变
    
    # 3. Y轴拖拽：按住"Y轴拖拽键"（Y_GRAB_KEY，需提前定义）时，仅沿Y轴移动选中对象
    elif self.window.is_key_pressed(ord(Y_GRAB_KEY)):
        self.selection.set_y(diff[1])  # 只修改Y坐标，X/Z坐标保持不变


def handle_resizing(self, point: Vect3):
    # 如果未初始化缩放参考点（未执行prepare_resizing），则不处理缩放
    if not hasattr(self, "scale_about_point"):
        return
    
    # 计算当前鼠标位置到缩放参考点的向量（用于计算缩放比例）
    vect = point - self.scale_about_point
    
    # 1. 非等比缩放：按住Ctrl键时，分别沿X/Y轴独立缩放
    if self.window.is_key_pressed(PygletWindowKeys.LCTRL):
        # 遍历X轴（0）和Y轴（1），分别计算缩放比例
        for i in (0, 1):
            # 缩放比例 = 当前鼠标向量在该轴的长度 / 初始参考向量在该轴的长度
            scalar = vect[i] / self.scale_ref_vect[i]
            # 按计算的比例缩放选中对象（仅沿当前轴）
            self.selection.rescale_to_fit(
                scalar * [self.scale_ref_width, self.scale_ref_height][i],  # 目标尺寸 = 比例 × 初始尺寸
                dim=i,  # 缩放维度（0=X轴，1=Y轴）
                about_point=self.scale_about_point,  # 围绕参考点缩放
                stretch=True,  # 允许拉伸（不保持宽高比）
            )
    
    # 2. 等比缩放：未按Ctrl键时，保持宽高比缩放
    else:
        # 缩放比例 = 当前鼠标向量的模长 / 初始参考向量的模长（确保X/Y轴缩放比例一致）
        scalar = get_norm(vect) / get_norm(self.scale_ref_vect)
        # 按比例修改选中对象的宽度（高度会自动等比调整）
        self.selection.set_width(
            scalar * self.scale_ref_width,  # 目标宽度 = 比例 × 初始宽度
            about_point=self.scale_about_point  # 围绕参考点缩放
        )

    def handle_sweeping_selection(self, point: Vect3):
    # 根据鼠标位置查找对应的可选择对象
    # point: 当前鼠标位置
    # search_set: 限定搜索范围为可选择对象集合
    # buff: 搜索缓冲区域大小（SMALL_BUFF为预设小值）
    mob = self.point_to_mobject(
        point,
        search_set=self.get_selection_search_set(),
        buff=SMALL_BUFF
    )
    # 如果找到对象，则将其添加到选中集合
    if mob is not None:
        self.add_to_selection(mob)

def choose_color(self, point: Vect3):
    # 准备搜索范围：场景中所有带点的子对象（排除不可交互对象）
    to_search = [
        sm
        for mobject in self.mobjects  # 遍历场景中所有对象
        for sm in mobject.family_members_with_points()  # 获取每个对象的所有带点子对象
        if mobject not in self.unselectables  # 排除不可交互对象
    ]
    # 根据鼠标位置在搜索范围内查找对象（通常是颜色面板中的颜色块）
    mob = self.point_to_mobject(point, to_search)
    # 如果找到对象，将选中的对象颜色设置为该对象的颜色
    if mob is not None:
        self.selection.set_color(mob.get_color())
    # 无论是否选择颜色，都移除颜色面板
    self.remove(self.color_palette)

def on_mouse_motion(self, point: Vect3, d_point: Vect3) -> None:
    # 调用父类的鼠标移动处理方法
    super().on_mouse_motion(point, d_point)
    # 将十字光标移动到鼠标当前位置（转换为固定框架坐标）
    self.crosshair.move_to(self.frame.to_fixed_frame_point(point))
    
    # 如果处于拖拽模式，处理选中对象的拖拽
    if self.is_grabbing:
        self.handle_grabbing(point)
    # 如果按住缩放键（RESIZE_KEY），处理选中对象的缩放
    elif self.window.is_key_pressed(ord(RESIZE_KEY)):
        self.handle_resizing(point)
    # 如果同时按住选择键（SELECT_KEY）和Shift键，处理扫选（鼠标划过即选中）
    elif self.window.is_key_pressed(ord(SELECT_KEY)) and self.window.is_key_pressed(PygletWindowKeys.LSHIFT):
        self.handle_sweeping_selection(point)

def on_mouse_drag(
    self,
    point: Vect3,
    d_point: Vect3,
    buttons: int,
    modifiers: int
) -> None:
    # 调用父类的鼠标拖拽处理方法
    super().on_mouse_drag(point, d_point, buttons, modifiers)
    # 在拖拽过程中，保持十字光标跟随鼠标位置（转换为固定框架坐标）
    self.crosshair.move_to(self.frame.to_fixed_frame_point(point))

def on_mouse_release(self, point: Vect3, button: int, mods: int) -> None:
    # 调用父类的鼠标释放处理方法
    super().on_mouse_release(point, button, mods)
    # 如果颜色面板在场景中（即处于颜色选择状态）
    if self.color_palette in self.mobjects:
        # 根据鼠标释放位置选择颜色
        self.choose_color(point)
    else:
        # 否则清除当前选中状态
        self.clear_selection()

# 复制用于重建状态的代码
def copy_frame_positioning(self):
    # 获取当前框架（通常是相机视图框架）
    frame = self.frame
    # 获取框架中心坐标
    center = frame.get_center()
    # 获取框架高度
    height = frame.get_height()
    # 获取框架的欧拉角（旋转角度）
    angles = frame.get_euler_angles()

    # 构建reorient函数调用字符串（用于重建当前视图状态）
    call = f"reorient("
    # 将弧度转换为度并取整
    theta, phi, gamma = (angles / DEG).astype(int)
    call += f"{theta}, {phi}, {gamma}"  # 添加旋转角度参数
    # 如果中心坐标不为原点，添加中心坐标参数
    if any(center != 0):
        call += f", {tuple(np.round(center, 2))}"
    # 如果高度不等于默认框架高度，添加高度参数
    if height != FRAME_HEIGHT:
        call += ", {:.2f}".format(height)
    call += ")"  # 闭合函数调用
    # 将构建的函数调用复制到剪贴板
    pyperclip.copy(call)

def copy_cursor_position(self):
    # 获取鼠标当前位置并四舍五入保留两位小数，转换为元组字符串
    # 将该字符串复制到剪贴板（用于快速获取光标坐标）
    pyperclip.copy(str(tuple(self.mouse_point.get_center().round(2))))