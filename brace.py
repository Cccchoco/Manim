# 从 __future__ 导入 annotations，这是为了让类型注解（type hints）可以在定义时直接使用类名本身，
# 而无需等待类完全定义，主要用于解决前向引用（forward references）的问题。
from __future__ import annotations

# 导入 Python 标准库 math，用于数学计算。
import math
# 导入 Python 标准库 copy，用于对象的复制（浅拷贝/深拷贝）。
import copy

# 导入 NumPy 库，并简写为 np，用于高效的数值计算和数组操作。
import numpy as np

# 从 manimlib 的 constants 模块导入常用的常量。
# DEFAULT_MOBJECT_TO_MOBJECT_BUFF：Mobject 之间的默认间距。
# SMALL_BUFF：一个较小的间距值。
from manimlib.constants import DEFAULT_MOBJECT_TO_MOBJECT_BUFF, SMALL_BUFF

# 从 manimlib 的 constants 模块导入方向向量常量。
# DOWN, LEFT, ORIGIN, RIGHT, DL, DR, UL, UP 分别表示下、左、原点、右、左下、右下、左上、上。
from manimlib.constants import DOWN, LEFT, ORIGIN, RIGHT, DL, DR, UL, UP

# 从 manimlib 的 constants 模块导入圆周率 PI。
from manimlib.constants import PI

# 从 manimlib 的 animation.composition 模块导入 AnimationGroup，
# 它用于将多个动画组合在一起，同时或按顺序播放。
from manimlib.animation.composition import AnimationGroup

# 从 manimlib 的 animation.fading 模块导入 FadeIn，
# 这是一个让 Mobject 淡入的动画效果。
from manimlib.animation.fading import FadeIn

# 从 manimlib 的 animation.growing 模块导入 GrowFromCenter，
# 这是一个从中心向外生长的动画效果。
from manimlib.animation.growing import GrowFromCenter

# 从 manimlib.mobject.svg.tex_mobject 导入 Tex 和 TexText，
# 它们用于处理 LaTeX 格式的文本，Tex 适合单行公式，TexText 适合多行或段落。
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.tex_mobject import TexText

# 从 manimlib.mobject.svg.text_mobject 导入 Text，
# 用于处理普通文本（非 LaTeX）。
from manimlib.mobject.svg.text_mobject import Text

# 从 manimlib.mobject.types.vectorized_mobject 导入 VGroup 和 VMobject，
# VGroup 是用于组合多个 Mobject 的容器，VMobject 是矢量图形对象的基类。
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject

# 从 manimlib.utils.iterables 导入 listify，
# 这是一个工具函数，用于将输入转换为列表（如果输入不是列表）。
from manimlib.utils.iterables import listify

# 从 manimlib.utils.space_ops 导入 get_norm，
# 用于计算向量的范数（长度）。
from manimlib.utils.space_ops import get_norm

# 从 typing 模块导入 TYPE_CHECKING，
# 这是一个常量，在代码运行时为 False，但在类型检查工具（如 mypy）分析代码时为 True，
# 常用于在不影响运行时性能的情况下进行类型注解相关的导入。
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterable

    from manimlib.animation.animation import Animation
    from manimlib.mobject.mobject import Mobject
    from manimlib.typing import Vect3


# 定义一个名为 Brace 的类，它继承自 Tex 类。
# 这意味着 Brace 拥有 Tex 的所有功能（如显示 LaTeX 文本），并在此基础上添加了新的功能。
class Brace(Tex):
    # 定义类的构造方法。
    def __init__(
        self,
        mobject: Mobject,      # 参数1: 一个 Mobject 对象，这是花括号将要“支撑”的对象。
        direction: Vect3 = DOWN, # 参数2: 花括号伸出的方向，默认为向下 (DOWN)。
        buff: float = 0.2,     # 参数3: 花括号与被支撑对象之间的缓冲距离（空隙），默认为 0.2。
        tex_string: str = R"\underbrace{\qquad}", # 参数4: 用于生成花括号的 LaTeX 字符串。
                                                  # \underbrace 是一个 LaTeX 命令，用于在表达式下方放置一个大花括号。
                                                  # {\qquad} 是一个占位符，提供了初始的宽度。
        **kwargs               # 参数5: 其他所有传给父类 Tex 的关键字参数（如颜色、字体大小等）。
    ):
        # 调用父类 Tex 的构造方法，用指定的 LaTeX 字符串和其他参数来创建这个花括号对象。
        # 此时，self 代表的就是那个 LaTeX 花括号。
        super().__init__(tex_string, **kwargs)

        # --- 核心定位逻辑开始 ---

        # 1. 计算旋转角度
        # direction[:2] 获取方向向量的 x 和 y 分量。
        # math.atan2(y, x) 计算该向量与正 x 轴的夹角。
        # -math.atan2(...) 取反，得到花括号应该旋转的角度。
        # + PI (π) 是为了将花括号的开口方向调整到与 `direction` 完全相反的方向。
        # 例如，如果 direction 是 DOWN (0, -1, 0)，那么 angle 的结果会是 0，花括号保持水平。
        # 如果 direction 是 LEFT (-1, 0, 0)，angle 的结果会是 π/2，花括号会向左旋转 90 度。
        angle = -math.atan2(*direction[:2]) + PI

        # 2. 临时旋转被支撑的对象，以便于计算宽度
        # 将被支撑的 mobject 旋转 -angle。
        # 这一步是一个“技巧”：我们临时将 mobject 旋转，使得它的“宽度”方向与花括号的“宽度”方向（水平方向）对齐。
        # 这样，我们就可以方便地通过 get_corner 来获取其在水平方向上的左右边界。
        # about_point=ORIGIN 表示绕坐标系原点旋转。
        mobject.rotate(-angle, about_point=ORIGIN)

        # 3. 计算被支撑对象的宽度
        # 获取 mobject 旋转后的左下角 (DL: Down Left) 坐标。
        left = mobject.get_corner(DL)
        # 获取 mobject 旋转后的右下角 (DR: Down Right) 坐标。
        right = mobject.get_corner(DR)
        # 用右下角的 x 坐标减去左下角的 x 坐标，得到 mobject 在水平方向上的实际宽度。
        target_width = right[0] - left[0]

        # 4. 调整花括号自身的大小和位置
        # np.argmin(...) 找到花括号上 y 坐标最小的点的索引。
        # 对于 \underbrace，这个点就是花括号的“尖端”。
        self.tip_point_index = np.argmin(self.get_all_points()[:, 1])
        # 根据之前计算的 target_width，设置花括号的初始宽度。
        # 这个方法内部会调整 LaTeX 公式的缩放比例，使其宽度匹配 target_width。
        self.set_initial_width(target_width)
        # 将花括号移动到正确的位置。
        # self.get_corner(UL) 是花括号自身的左上角。
        # left - self.get_corner(UL) 计算出一个位移向量，使得花括号的左上角与 mobject 的左下角对齐。
        # + buff * DOWN 在 direction 方向上（默认为下）增加一个缓冲距离。
        self.shift(left - self.get_corner(UL) + buff * DOWN)

        # 5. 恢复所有对象的正确朝向
        # 遍历 mobject 和 self (花括号)。
        # 将它们都旋转回原来的角度 `angle`。
        # 因为之前 mobject 被旋转了 -angle，现在旋转 +angle 就恢复了原位。
        # 花括号也随之旋转，这样它就倾斜到了正确的方向，完美地“支撑”在 mobject 的旁边。
        for mob in mobject, self:
            mob.rotate(angle, about_point=ORIGIN)

    def set_initial_width(self, width: float):
        """
        调整括号的初始宽度。

        这个方法用于将括号的宽度设置为一个指定值。它的核心逻辑是：
        如果目标宽度大于当前宽度，则通过向两侧延伸来增加宽度；
        如果目标宽度小于或等于当前宽度，则直接调用父类的 `set_width` 方法进行缩放。

        Args:
            width (float): 括号期望的最终宽度。

        Returns:
            self: 返回自身实例，以便支持链式调用。
        """
    # 计算目标宽度与当前宽度的差值.。。。
    width_diff = width - self.get_width()

    # 如果目标宽度大于当前宽度，需要进行扩展
    if width_diff > 0:
            for tip, rect, vect in [(self[0], self[1], RIGHT), (self[5], self[4], LEFT)]:
                rect.set_width(
                    width_diff / 2 + rect.get_width(),
                    about_edge=vect, stretch=True
                )
                tip.shift(-width_diff / 2 * vect)
    else:
            self.set_width(width, stretch=True)
    return self

    def put_at_tip(
        self,
        mob: Mobject,
        use_next_to: bool = True,
        **kwargs
    ):
        if use_next_to:
            mob.next_to(
                self.get_tip(),
                np.round(self.get_direction()),
                **kwargs
            )
        else:
            mob.move_to(self.get_tip())
            buff = kwargs.get("buff", DEFAULT_MOBJECT_TO_MOBJECT_BUFF)
            shift_distance = mob.get_width() / 2.0 + buff
            mob.shift(self.get_direction() * shift_distance)
        return self

    def get_text(self, text: str, **kwargs) -> Text:
        buff = kwargs.pop("buff", SMALL_BUFF)
        text_mob = Text(text, **kwargs)
        self.put_at_tip(text_mob, buff=buff)
        return text_mob

    def get_tex(self, *tex: str, **kwargs) -> Tex:
        buff = kwargs.pop("buff", SMALL_BUFF)
        tex_mob = Tex(*tex, **kwargs)
        self.put_at_tip(tex_mob, buff=buff)
        return tex_mob

    def get_tip(self) -> np.ndarray:
        # Very specific to the LaTeX representation
        # of a brace, but it's the only way I can think
        # of to get the tip regardless of orientation.
        return self.get_all_points()[self.tip_point_index]

    def get_direction(self) -> np.ndarray:
        vect = self.get_tip() - self.get_center()
        return vect / get_norm(vect)


class BraceLabel(VMobject):
    label_constructor: type = Tex

    def __init__(
        self,
        obj: VMobject | list[VMobject],
        text: str | Iterable[str],
        brace_direction: np.ndarray = DOWN,
        label_scale: float = 1.0,
        label_buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFF,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.brace_direction = brace_direction
        self.label_scale = label_scale
        self.label_buff = label_buff

        if isinstance(obj, list):
            obj = VGroup(*obj)
        self.brace = Brace(obj, brace_direction, **kwargs)

        self.label = self.label_constructor(*listify(text), **kwargs)
        self.label.scale(self.label_scale)

        self.brace.put_at_tip(self.label, buff=self.label_buff)
        self.set_submobjects([self.brace, self.label])

    def creation_anim(
        self,
        label_anim: Animation = FadeIn,
        brace_anim: Animation = GrowFromCenter
    ) -> AnimationGroup:
        return AnimationGroup(brace_anim(self.brace), label_anim(self.label))

    def shift_brace(self, obj: VMobject | list[VMobject], **kwargs):
        if isinstance(obj, list):
            obj = VMobject(*obj)
        self.brace = Brace(obj, self.brace_direction, **kwargs)
        self.brace.put_at_tip(self.label)
        self.submobjects[0] = self.brace
        return self

    def change_label(self, *text: str, **kwargs):
        self.label = self.label_constructor(*text, **kwargs)
        if self.label_scale != 1:
            self.label.scale(self.label_scale)

        self.brace.put_at_tip(self.label)
        self.submobjects[1] = self.label
        return self

    def change_brace_label(self, obj: VMobject | list[VMobject], *text: str):
        self.shift_brace(obj)
        self.change_label(*text)
        return self

    def copy(self):
        copy_mobject = copy.copy(self)
        copy_mobject.brace = self.brace.copy()
        copy_mobject.label = self.label.copy()
        copy_mobject.set_submobjects([copy_mobject.brace, copy_mobject.label])

        return copy_mobject


class BraceText(BraceLabel):
    label_constructor: type = TexText


class LineBrace(Brace):
    def __init__(self, line: Line, direction=UP, **kwargs):
        angle = line.get_angle()
        line.rotate(-angle)
        super().__init__(line, direction, **kwargs)
        line.rotate(angle)
        self.rotate(angle, about_point=line.get_center())
