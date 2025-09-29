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
        self.selection = Group()
        self.selection_highlight = self.get_selection_highlight()
        self.selection_rectangle = self.get_selection_rectangle()
        self.crosshair = self.get_crosshair()
        self.information_label = self.get_information_label()
        self.color_palette = self.get_color_palette()
        self.unselectables = [
            self.selection,
            self.selection_highlight,
            self.selection_rectangle,
            self.crosshair,
            self.information_label,
            self.camera.frame
        ]
        self.select_top_level_mobs = True
        self.regenerate_selection_search_set()

        self.is_selecting = False
        self.is_grabbing = False

        self.add(self.selection_highlight)

    def get_selection_rectangle(self):
        rect = Rectangle(
            stroke_color=self.selection_rectangle_stroke_color,
            stroke_width=self.selection_rectangle_stroke_width,
        )
        rect.fix_in_frame()
        rect.fixed_corner = ORIGIN
        rect.add_updater(self.update_selection_rectangle)
        return rect

    def update_selection_rectangle(self, rect: Rectangle):
        p1 = rect.fixed_corner
        p2 = self.frame.to_fixed_frame_point(self.mouse_point.get_center())
        rect.set_points_as_corners([
            p1, np.array([p2[0], p1[1], 0]),
            p2, np.array([p1[0], p2[1], 0]),
            p1,
        ])
        return rect

    def get_selection_highlight(self):
        result = Group()
        result.tracked_mobjects = []
        result.add_updater(self.update_selection_highlight)
        return result

    def update_selection_highlight(self, highlight: Mobject):
        if set(highlight.tracked_mobjects) == set(self.selection):
            return

        # Otherwise, refresh contents of highlight
        highlight.tracked_mobjects = list(self.selection)
        highlight.set_submobjects([
            self.get_highlight(mob)
            for mob in self.selection
        ])
        try:
            index = min((
                i for i, mob in enumerate(self.mobjects)
                for sm in self.selection
                if sm in mob.get_family()
            ))
            self.mobjects.remove(highlight)
            self.mobjects.insert(index - 1, highlight)
        except ValueError:
            pass

    def get_crosshair(self):
        lines = VMobject().replicate(2)
        lines[0].set_points([LEFT, ORIGIN, RIGHT])
        lines[1].set_points([UP, ORIGIN, DOWN])
        crosshair = VGroup(*lines)

        crosshair.set_width(self.crosshair_width)
        crosshair.set_style(**self.crosshair_style)
        crosshair.set_animating_status(True)
        crosshair.fix_in_frame()
        return crosshair

    def get_color_palette(self):
        palette = VGroup(*(
            Square(fill_color=color, fill_opacity=1, side_length=1)
            for color in self.palette_colors
        ))
        palette.set_stroke(width=0)
        palette.arrange(RIGHT, buff=0.5)
        palette.set_width(FRAME_WIDTH - 0.5)
        palette.to_edge(DOWN, buff=SMALL_BUFF)
        palette.fix_in_frame()
        return palette

    def get_information_label(self):
        loc_label = VGroup(*(
            DecimalNumber(**self.cursor_location_config)
            for n in range(3)
        ))

        def update_coords(loc_label):
            for mob, coord in zip(loc_label, self.mouse_point.get_location()):
                mob.set_value(coord)
            loc_label.arrange(RIGHT, buff=loc_label.get_height())
            loc_label.to_corner(DR, buff=SMALL_BUFF)
            loc_label.fix_in_frame()
            return loc_label

        loc_label.add_updater(update_coords)

        time_label = DecimalNumber(0, **self.time_label_config)
        time_label.to_corner(DL, buff=SMALL_BUFF)
        time_label.fix_in_frame()
        time_label.add_updater(lambda m, dt: m.increment_value(dt))

        return VGroup(loc_label, time_label)

    # Overrides
    def get_state(self):
        return SceneState(self, ignore=[
            self.selection_highlight,
            self.selection_rectangle,
            self.crosshair,
        ])

    def restore_state(self, scene_state: SceneState):
        super().restore_state(scene_state)
        self.mobjects.insert(0, self.selection_highlight)

    def add(self, *mobjects: Mobject):
        super().add(*mobjects)
        self.regenerate_selection_search_set()

    def remove(self, *mobjects: Mobject):
        super().remove(*mobjects)
        self.regenerate_selection_search_set()

    def remove_all_except(self, *mobjects_to_keep : Mobject):
        super().remove_all_except(*mobjects_to_keep)
        self.regenerate_selection_search_set()

    # Related to selection

    def toggle_selection_mode(self):
        self.select_top_level_mobs = not self.select_top_level_mobs
        self.refresh_selection_scope()
        self.regenerate_selection_search_set()

    def get_selection_search_set(self) -> list[Mobject]:
        return self.selection_search_set

    def regenerate_selection_search_set(self):
        selectable = list(filter(
            lambda m: m not in self.unselectables,
            self.mobjects
        ))
        if self.select_top_level_mobs:
            self.selection_search_set = selectable
        else:
            self.selection_search_set = [
                submob
                for mob in selectable
                for submob in mob.family_members_with_points()
            ]

    def refresh_selection_scope(self):
        curr = list(self.selection)
        if self.select_top_level_mobs:
            self.selection.set_submobjects([
                mob
                for mob in self.mobjects
                if any(sm in mob.get_family() for sm in curr)
            ])
            self.selection.refresh_bounding_box(recurse_down=True)
        else:
            self.selection.set_submobjects(
                extract_mobject_family_members(
                    curr, exclude_pointless=True,
                )
            )

    def get_corner_dots(self, mobject: Mobject) -> Mobject:
        dots = DotCloud(**self.corner_dot_config)
        radius = float(self.corner_dot_config["radius"])
        if mobject.get_depth() < 1e-2:
            vects = [DL, UL, UR, DR]
        else:
            vects = np.array(list(it.product(*3 * [[-1, 1]])))
        dots.add_updater(lambda d: d.set_points([
            mobject.get_corner(v) + v * radius
            for v in vects
        ]))
        return dots

    def get_highlight(self, mobject: Mobject) -> Mobject:
        if isinstance(mobject, VMobject) and mobject.has_points() and not self.select_top_level_mobs:
            length = max([mobject.get_height(), mobject.get_width()])
            result = VHighlight(
                mobject,
                max_stroke_addition=min([50 * length, 10]),
            )
            result.add_updater(lambda m: m.replace(mobject, stretch=True))
            return result
        elif isinstance(mobject, DotCloud):
            return Mobject()
        else:
            return self.get_corner_dots(mobject)

    def add_to_selection(self, *mobjects: Mobject):
        mobs = list(filter(
            lambda m: m not in self.unselectables and m not in self.selection,
            mobjects
        ))
        if len(mobs) == 0:
            return
        self.selection.add(*mobs)
        for mob in mobs:
            mob.set_animating_status(True)

    def toggle_from_selection(self, *mobjects: Mobject):
        for mob in mobjects:
            if mob in self.selection:
                self.selection.remove(mob)
                mob.set_animating_status(False)
                mob.refresh_bounding_box()
            else:
                self.add_to_selection(mob)

    def clear_selection(self):
        for mob in self.selection:
            mob.set_animating_status(False)
            mob.refresh_bounding_box()
        self.selection.set_submobjects([])

    def disable_interaction(self, *mobjects: Mobject):
        for mob in mobjects:
            for sm in mob.get_family():
                self.unselectables.append(sm)
        self.regenerate_selection_search_set()

    def enable_interaction(self, *mobjects: Mobject):
        for mob in mobjects:
            for sm in mob.get_family():
                if sm in self.unselectables:
                    self.unselectables.remove(sm)

    # Functions for keyboard actions

    def copy_selection(self):
        names = []
        shell = get_ipython()
        for mob in self.selection:
            name = str(id(mob))
            if shell is None:
                continue
            for key, value in shell.user_ns.items():
                if mob is value:
                    name = key
            names.append(name)
        pyperclip.copy(", ".join(names))

    def paste_selection(self):
        clipboard_str = pyperclip.paste()
        # Try pasting a mobject
        try:
            ids = map(int, clipboard_str.split(","))
            mobs = map(self.id_to_mobject, ids)
            mob_copies = [m.copy() for m in mobs if m is not None]
            self.clear_selection()
            self.play(*(
                FadeIn(mc, run_time=0.5, scale=1.5)
                for mc in mob_copies
            ))
            self.add_to_selection(*mob_copies)
            return
        except ValueError:
            pass
        # Otherwise, treat as tex or text
        if set("\\^=+").intersection(clipboard_str):  # Proxy to text for LaTeX
            try:
                new_mob = Tex(clipboard_str)
            except LatexError:
                return
        else:
            new_mob = Text(clipboard_str)
        self.clear_selection()
        self.add(new_mob)
        self.add_to_selection(new_mob)

    def delete_selection(self):
        self.remove(*self.selection)
        self.clear_selection()

    def enable_selection(self):
        self.is_selecting = True
        self.add(self.selection_rectangle)
        self.selection_rectangle.fixed_corner = self.frame.to_fixed_frame_point(
            self.mouse_point.get_center()
        )

    def gather_new_selection(self):
        self.is_selecting = False
        if self.selection_rectangle in self.mobjects:
            self.remove(self.selection_rectangle)
            additions = []
            for mob in reversed(self.get_selection_search_set()):
                if self.selection_rectangle.is_touching(mob):
                    additions.append(mob)
                    if self.selection_rectangle.get_arc_length() < 1e-2:
                        break
            self.toggle_from_selection(*additions)

    def prepare_grab(self):
        mp = self.mouse_point.get_center()
        self.mouse_to_selection = mp - self.selection.get_center()
        self.is_grabbing = True

    def prepare_resizing(self, about_corner=False):
        center = self.selection.get_center()
        mp = self.mouse_point.get_center()
        if about_corner:
            self.scale_about_point = self.selection.get_corner(center - mp)
        else:
            self.scale_about_point = center
        self.scale_ref_vect = mp - self.scale_about_point
        self.scale_ref_width = self.selection.get_width()
        self.scale_ref_height = self.selection.get_height()

    def toggle_color_palette(self):
        if len(self.selection) == 0:
            return
        if self.color_palette not in self.mobjects:
            self.save_state()
            self.add(self.color_palette)
        else:
            self.remove(self.color_palette)

    def display_information(self, show=True):
        if show:
            self.add(self.information_label)
        else:
            self.remove(self.information_label)

    def group_selection(self):
        group = self.get_group(*self.selection)
        self.add(group)
        self.clear_selection()
        self.add_to_selection(group)

    def ungroup_selection(self):
        pieces = []
        for mob in list(self.selection):
            self.remove(mob)
            pieces.extend(list(mob))
        self.clear_selection()
        self.add(*pieces)
        self.add_to_selection(*pieces)

    def nudge_selection(self, vect: np.ndarray, large: bool = False):
        nudge = self.selection_nudge_size
        if large:
            nudge *= 10
        self.selection.shift(nudge * vect)

    # Key actions
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        super().on_key_press(symbol, modifiers)
        char = chr(symbol)
        if char == SELECT_KEY and (modifiers & ALL_MODIFIERS) == 0:
            self.enable_selection()
        if char == UNSELECT_KEY:
            self.clear_selection()
        elif char in GRAB_KEYS and (modifiers & ALL_MODIFIERS) == 0:
            self.prepare_grab()
        elif char == RESIZE_KEY and (modifiers & PygletWindowKeys.MOD_SHIFT):
            self.prepare_resizing(about_corner=((modifiers & PygletWindowKeys.MOD_SHIFT) > 0))
        elif symbol == PygletWindowKeys.LSHIFT:
            if self.window.is_key_pressed(ord("t")):
                self.prepare_resizing(about_corner=True)
        elif char == COLOR_KEY and (modifiers & ALL_MODIFIERS) == 0:
            self.toggle_color_palette()
        elif char == INFORMATION_KEY and (modifiers & ALL_MODIFIERS) == 0:
            self.display_information()
        elif char == "c" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
            self.copy_selection()
        elif char == "v" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
            self.paste_selection()
        elif char == "x" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
            self.copy_selection()
            self.delete_selection()
        elif symbol == PygletWindowKeys.BACKSPACE:
            self.delete_selection()
        elif char == "a" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
            self.clear_selection()
            self.add_to_selection(*self.mobjects)
        elif char == "g" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
            self.group_selection()
        elif char == "g" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL | PygletWindowKeys.MOD_SHIFT)):
            self.ungroup_selection()
        elif char == "t" and (modifiers & (PygletWindowKeys.MOD_COMMAND | PygletWindowKeys.MOD_CTRL)):
            self.toggle_selection_mode()
        elif char == "d" and (modifiers & PygletWindowKeys.MOD_SHIFT):
            self.copy_frame_positioning()
        elif char == "c" and (modifiers & PygletWindowKeys.MOD_SHIFT):
            self.copy_cursor_position()
        elif symbol in ARROW_SYMBOLS:
            self.nudge_selection(
                vect=[LEFT, UP, RIGHT, DOWN][ARROW_SYMBOLS.index(symbol)],
                large=(modifiers & PygletWindowKeys.MOD_SHIFT),
            )
        # Adding crosshair
        if char == CURSOR_KEY:
            if self.crosshair in self.mobjects:
                self.remove(self.crosshair)
            else:
                self.add(self.crosshair)
        if char == SELECT_KEY:
            self.add(self.crosshair)

        # Conditions for saving state
        if char in [GRAB_KEY, X_GRAB_KEY, Y_GRAB_KEY, RESIZE_KEY]:
            self.save_state()

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        super().on_key_release(symbol, modifiers)
        if chr(symbol) == SELECT_KEY:
            self.gather_new_selection()
        if chr(symbol) in GRAB_KEYS:
            self.is_grabbing = False
        elif chr(symbol) == INFORMATION_KEY:
            self.display_information(False)
        elif symbol == PygletWindowKeys.LSHIFT and self.window.is_key_pressed(ord(RESIZE_KEY)):
            self.prepare_resizing(about_corner=False)

    # Mouse actions
    def handle_grabbing(self, point: Vect3):
        diff = point - self.mouse_to_selection
        if self.window.is_key_pressed(ord(GRAB_KEY)):
            self.selection.move_to(diff)
        elif self.window.is_key_pressed(ord(X_GRAB_KEY)):
            self.selection.set_x(diff[0])
        elif self.window.is_key_pressed(ord(Y_GRAB_KEY)):
            self.selection.set_y(diff[1])

    def handle_resizing(self, point: Vect3):
        if not hasattr(self, "scale_about_point"):
            return
        vect = point - self.scale_about_point
        if self.window.is_key_pressed(PygletWindowKeys.LCTRL):
            for i in (0, 1):
                scalar = vect[i] / self.scale_ref_vect[i]
                self.selection.rescale_to_fit(
                    scalar * [self.scale_ref_width, self.scale_ref_height][i],
                    dim=i,
                    about_point=self.scale_about_point,
                    stretch=True,
                )
        else:
            scalar = get_norm(vect) / get_norm(self.scale_ref_vect)
            self.selection.set_width(
                scalar * self.scale_ref_width,
                about_point=self.scale_about_point
            )

    def handle_sweeping_selection(self, point: Vect3):
        mob = self.point_to_mobject(
            point,
            search_set=self.get_selection_search_set(),
            buff=SMALL_BUFF
        )
        if mob is not None:
            self.add_to_selection(mob)

    def choose_color(self, point: Vect3):
        # Search through all mobject on the screen, not just the palette
        to_search = [
            sm
            for mobject in self.mobjects
            for sm in mobject.family_members_with_points()
            if mobject not in self.unselectables
        ]
        mob = self.point_to_mobject(point, to_search)
        if mob is not None:
            self.selection.set_color(mob.get_color())
        self.remove(self.color_palette)

    def on_mouse_motion(self, point: Vect3, d_point: Vect3) -> None:
        super().on_mouse_motion(point, d_point)
        self.crosshair.move_to(self.frame.to_fixed_frame_point(point))
        if self.is_grabbing:
            self.handle_grabbing(point)
        elif self.window.is_key_pressed(ord(RESIZE_KEY)):
            self.handle_resizing(point)
        elif self.window.is_key_pressed(ord(SELECT_KEY)) and self.window.is_key_pressed(PygletWindowKeys.LSHIFT):
            self.handle_sweeping_selection(point)

    def on_mouse_drag(
        self,
        point: Vect3,
        d_point: Vect3,
        buttons: int,
        modifiers: int
    ) -> None:
        super().on_mouse_drag(point, d_point, buttons, modifiers)
        self.crosshair.move_to(self.frame.to_fixed_frame_point(point))

    def on_mouse_release(self, point: Vect3, button: int, mods: int) -> None:
        super().on_mouse_release(point, button, mods)
        if self.color_palette in self.mobjects:
            self.choose_color(point)
        else:
            self.clear_selection()

    # Copying code to recreate state
    def copy_frame_positioning(self):
        frame = self.frame
        center = frame.get_center()
        height = frame.get_height()
        angles = frame.get_euler_angles()

        call = f"reorient("
        theta, phi, gamma = (angles / DEG).astype(int)
        call += f"{theta}, {phi}, {gamma}"
        if any(center != 0):
            call += f", {tuple(np.round(center, 2))}"
        if height != FRAME_HEIGHT:
            call += ", {:.2f}".format(height)
        call += ")"
        pyperclip.copy(call)

    def copy_cursor_position(self):
        pyperclip.copy(str(tuple(self.mouse_point.get_center().round(2))))
