# 启用Python 3.7+的注解向前向兼容支持，允许在类型注解中使用尚未定义的类
from __future__ import annotations

# 导入numpy库，用于数值计算和数组操作
import numpy as np

# 导入动画相关类
from manimlib.animation.animation import Animation  # 基础动画类
from manimlib.animation.composition import AnimationGroup  # 动画组合类
from manimlib.animation.composition import Succession  # 顺序执行动画类
from manimlib.animation.creation import ShowCreation  # 绘制创建动画类
from manimlib.animation.creation import ShowPartial  # 部分显示动画类
from manimlib.animation.fading import FadeOut  # 淡出动画类
from manimlib.animation.fading import FadeIn  # 淡入动画类
from manimlib.animation.movement import Homotopy  # 同伦变换动画类
from manimlib.animation.transform import Transform  # 对象变换动画类

# 导入常量
from manimlib.constants import FRAME_X_RADIUS, FRAME_Y_RADIUS  # 帧的X/Y半径
from manimlib.constants import ORIGIN, RIGHT, UP  # 原点坐标及方向向量
from manimlib.constants import SMALL_BUFF  # 小间距常量
from manimlib.constants import DEG  # 角度单位（度）
from manimlib.constants import TAU  # 数学常量τ=2π
from manimlib.constants import GREY, YELLOW  # 颜色常量

# 导入图形对象类
from manimlib.mobject.geometry import Circle  # 圆形类
from manimlib.mobject.geometry import Dot  # 点形类
from manimlib.mobject.geometry import Line  # 线段类
from manimlib.mobject.shape_matchers import SurroundingRectangle  # 包围矩形类
from manimlib.mobject.shape_matchers import Underline  # 下划线类
from manimlib.mobject.types.vectorized_mobject import VMobject  # 矢量图形对象类
from manimlib.mobject.types.vectorized_mobject import VGroup  # 矢量图形组合类

# 导入工具函数
from manimlib.utils.bezier import interpolate  # 贝塞尔插值函数
from manimlib.utils.rate_functions import smooth  # 平滑速率函数
from manimlib.utils.rate_functions import squish_rate_func  # 压缩速率函数
from manimlib.utils.rate_functions import there_and_back  # 往返速率函数
from manimlib.utils.rate_functions import wiggle  # 摆动速率函数

# 导入类型检查相关模块
from typing import TYPE_CHECKING

# 条件导入，仅在类型检查时执行（运行时不生效）
# 用于解决循环导入问题，同时提供完整的类型提示支持
if TYPE_CHECKING:
    from typing import Callable  # 可调用对象类型注解
    from manimlib.typing import ManimColor  # Manim颜色类型
    from manimlib.mobject.mobject import Mobject  # 基础可移动对象类


class FocusOn(Transform):
    """
    继承自Transform动画类，用于创建一个聚焦效果动画
    表现为从屏幕边缘向焦点位置收缩的半透明遮罩，突出显示焦点区域
    """
    def __init__(
        self,
        focus_point: np.ndarray | Mobject,  # 聚焦点，可以是坐标数组或Mobject对象
        opacity: float = 0.2,  # 遮罩的不透明度
        color: ManimColor = GREY,  # 遮罩的颜色
        run_time: float = 2,  # 动画持续时间
        remover: bool = True,  # 动画结束后是否移除遮罩
        **kwargs  # 传递给父类Transform的其他参数
    ):
        # 保存聚焦点、不透明度和颜色为实例属性
        self.focus_point = focus_point
        self.opacity = opacity
        self.color = color
        # 调用父类Transform的初始化方法
        # 先以空白的VMobject初始化，具体的起始和目标对象由后续方法创建
        super().__init__(VMobject(), run_time=run_time, remover=remover,** kwargs)

    def create_target(self) -> Dot:
        """创建动画的目标对象（最终状态）"""
        # 创建一个半径为0的点（实际上不可见）
        little_dot = Dot(radius=0)
        # 设置点的填充颜色和不透明度
        little_dot.set_fill(self.color, opacity=self.opacity)
        # 添加更新器，确保点始终跟随聚焦点移动
        little_dot.add_updater(lambda d: d.move_to(self.focus_point))
        return little_dot

    def create_starting_mobject(self) -> Dot:
        """创建动画的起始对象（初始状态）"""
        # 创建一个覆盖整个屏幕的大圆点作为起始遮罩
        return Dot(
            radius=FRAME_X_RADIUS + FRAME_Y_RADIUS,  # 半径为屏幕宽高半径之和，确保覆盖全屏
            stroke_width=0,  # 无边框
            fill_color=self.color,  # 填充颜色
            fill_opacity=0,  # 初始完全透明
        )


class Indicate(Transform):
    """
    继承自Transform动画类，用于创建"指示"效果动画
    表现为对象先放大变色，再恢复原状，起到强调突出的作用
    """
    def __init__(
        self,
        mobject: Mobject,  # 要进行指示动画的对象
        scale_factor: float = 1.2,  # 放大倍数，默认1.2倍
        color: ManimColor = YELLOW,  # 指示时的高亮颜色，默认黄色
        # 速率函数，默认使用there_and_back（去而复返），使动画先变后恢复
        rate_func: Callable[[float], float] = there_and_back,** kwargs  # 传递给父类Transform的其他参数
    ):
        # 保存放大倍数和高亮颜色为实例属性
        self.scale_factor = scale_factor
        self.color = color
        # 调用父类Transform的初始化方法，传入速率函数等参数
        super().__init__(mobject, rate_func=rate_func, **kwargs)

    def create_target(self) -> Mobject:
        """创建动画的目标对象（中间状态）"""
        # 复制原始对象作为目标对象的基础
        target = self.mobject.copy()
        # 按照指定倍数放大目标对象
        target.scale(self.scale_factor)
        # 将目标对象设置为高亮颜色
        target.set_color(self.color)
        return target


class Flash(AnimationGroup):
    """
    继承自AnimationGroup动画组类，用于创建"闪烁"效果动画
    表现为从指定点向外放射出多条线条，然后消失，类似闪光效果
    """
    def __init__(
        self,
        point: np.ndarray | Mobject,  # 闪光的中心点，可以是坐标数组或Mobject对象
        color: ManimColor = YELLOW,  # 闪光线条的颜色，默认黄色
        line_length: float = 0.2,  # 每条闪光线条的长度
        num_lines: int = 12,  # 闪光线条的数量
        flash_radius: float = 0.3,  # 闪光的初始半径（线条起点到中心的距离）
        line_stroke_width: float = 3.0,  # 线条的粗细
        run_time: float = 1.0,  # 动画持续时间
        **kwargs  # 传递给父类AnimationGroup的其他参数
    ):
        # 保存闪光效果的各项参数为实例属性
        self.point = point
        self.color = color
        self.line_length = line_length
        self.num_lines = num_lines
        self.flash_radius = flash_radius
        self.line_stroke_width = line_stroke_width

        # 创建闪光效果的所有线条
        self.lines = self.create_lines()
        # 为每条线条创建对应的动画
        animations = self.create_line_anims()
        # 调用父类AnimationGroup的初始化方法
        super().__init__(
            *animations,  # 展开所有线条的动画
            group=self.lines,  # 指定动画组的对象
            run_time=run_time,  # 动画持续时间
            **kwargs,  # 其他参数
        )

    def create_lines(self) -> VGroup:
        """创建组成闪光效果的所有线条"""
        # 创建一个向量图形组来管理所有线条
        lines = VGroup()
        # 按照角度均匀分布创建指定数量的线条
        # TAU是2π，代表360度，这里将圆周等分为num_lines份
        for angle in np.arange(0, TAU, TAU / self.num_lines):
            # 创建一条从原点到右侧指定长度的线段
            line = Line(ORIGIN, self.line_length * RIGHT)
            # 将线条移动到闪光半径的位置（线条起点距离中心的距离）
            line.shift((self.flash_radius - self.line_length) * RIGHT)
            # 绕原点旋转线条到当前角度，形成放射状分布
            line.rotate(angle, about_point=ORIGIN)
            # 将线条添加到图形组中
            lines.add(line)
        # 设置所有线条的样式（颜色和粗细）
        lines.set_stroke(
            color=self.color,
            width=self.line_stroke_width
        )
        # 添加更新器，确保所有线条始终围绕指定点（point）
        lines.add_updater(lambda l: l.move_to(self.point))
        return lines

    def create_line_anims(self) -> list[Animation]:
        """为每条线条创建显示后消失的动画"""
        # 为每条线创建ShowCreationThenDestruction动画
        # 该动画会先显示线条（从无到有），然后再让线条消失（从有到无）
        return [
            ShowCreationThenDestruction(line)
            for line in self.lines
        ]


class CircleIndicate(Transform):
    """
    继承自Transform动画类，用于创建圆形指示动画
    表现为围绕目标对象的圆形边框先放大再缩小，起到强调作用
    """
    def __init__(
        self,
        mobject: Mobject,  # 要被指示的目标对象
        scale_factor: float = 1.2,  # 圆形放大倍数，默认1.2倍
        # 速率函数，默认使用there_and_back（去而复返），使动画先放大后缩小
        rate_func: Callable[[float], float] = there_and_back,
        stroke_color: ManimColor = YELLOW,  # 圆形边框颜色，默认黄色
        stroke_width: float = 3.0,  # 圆形边框粗细
        remover: bool = True,  # 动画结束后是否移除圆形
        **kwargs  # 传递给父类Transform的其他参数
    ):
        # 创建一个圆形，设置其边框颜色和粗细
        circle = Circle(stroke_color=stroke_color, stroke_width=stroke_width)
        # 让圆形包围目标对象（调整大小以刚好包围目标）
        circle.surround(mobject)
        # 复制圆形作为初始状态对象，并将其边框宽度设为0（初始不可见）
        pre_circle = circle.copy().set_stroke(width=0)
        # 将初始圆形按缩放因子的倒数缩小（为后续放大动画做准备）
        pre_circle.scale(1 / scale_factor)
        # 调用父类Transform的初始化方法，将初始圆形变换为目标圆形
        super().__init__(
            pre_circle,  # 起始对象（缩小且不可见的圆形）
            circle,      # 目标对象（包围目标且可见的圆形）
            rate_func=rate_func,  # 应用速率函数
            remover=remover,      # 动画结束后移除圆形
            **kwargs              # 其他参数
        )


class ShowPassingFlash(ShowPartial):
    def __init__(
        self,
        mobject: Mobject,
        time_width: float = 0.1,
        remover: bool = True,
        **kwargs
    ):
        self.time_width = time_width
        super().__init__(
            mobject,
            remover=remover,
            **kwargs
        )

    def get_bounds(self, alpha: float) -> tuple[float, float]:
        tw = self.time_width
        upper = interpolate(0, 1 + tw, alpha)
        lower = upper - tw
        upper = min(upper, 1)
        lower = max(lower, 0)
        return (lower, upper)

    def finish(self) -> None:
        super().finish()
        for submob, start in self.get_all_families_zipped():
            submob.pointwise_become_partial(start, 0, 1)


class VShowPassingFlash(Animation):
    def __init__(
        self,
        vmobject: VMobject,
        time_width: float = 0.3,
        taper_width: float = 0.05,
        remover: bool = True,
        **kwargs
    ):
        self.time_width = time_width
        self.taper_width = taper_width
        super().__init__(vmobject, remover=remover, **kwargs)
        self.mobject = vmobject

    def taper_kernel(self, x):
        if x < self.taper_width:
            return x
        elif x > 1 - self.taper_width:
            return 1.0 - x
        return 1.0

    def begin(self) -> None:
        # Compute an array of stroke widths for each submobject
        # which tapers out at either end
        self.submob_to_widths = dict()
        for sm in self.mobject.get_family():
            widths = sm.get_stroke_widths()
            self.submob_to_widths[hash(sm)] = np.array([
                width * self.taper_kernel(x)
                for width, x in zip(widths, np.linspace(0, 1, len(widths)))
            ])
        super().begin()

    def interpolate_submobject(
        self,
        submobject: VMobject,
        starting_sumobject: None,
        alpha: float
    ) -> None:
        widths = self.submob_to_widths[hash(submobject)]

        # Create a gaussian such that 3 sigmas out on either side
        # will equals time_width
        tw = self.time_width
        sigma = tw / 6
        mu = interpolate(-tw / 2, 1 + tw / 2, alpha)
        xs = np.linspace(0, 1, len(widths))
        zs = (xs - mu) / sigma
        gaussian = np.exp(-0.5 * zs * zs)
        gaussian[abs(xs - mu) > 3 * sigma] = 0

        if len(widths * gaussian) !=0:
            submobject.set_stroke(width=widths * gaussian)


    def finish(self) -> None:
        super().finish()
        for submob, start in self.get_all_families_zipped():
            submob.match_style(start)


class FlashAround(VShowPassingFlash):
    def __init__(
        self,
        mobject: Mobject,
        time_width: float = 1.0,
        taper_width: float = 0.0,
        stroke_width: float = 4.0,
        color: ManimColor = YELLOW,
        buff: float = SMALL_BUFF,
        n_inserted_curves: int = 100,
        **kwargs
    ):
        path = self.get_path(mobject, buff)
        if mobject.is_fixed_in_frame():
            path.fix_in_frame()
        path.insert_n_curves(n_inserted_curves)
        path.set_points(path.get_points_without_null_curves())
        path.set_stroke(color, stroke_width)
        super().__init__(path, time_width=time_width, taper_width=taper_width, **kwargs)

    def get_path(self, mobject: Mobject, buff: float) -> SurroundingRectangle:
        return SurroundingRectangle(mobject, buff=buff)


class FlashUnder(FlashAround):
    def get_path(self, mobject: Mobject, buff: float) -> Underline:
        return Underline(mobject, buff=buff, stretch_factor=1.0)


class ShowCreationThenDestruction(ShowPassingFlash):
    def __init__(self, vmobject: VMobject, time_width: float = 2.0, **kwargs):
        super().__init__(vmobject, time_width=time_width, **kwargs)


class ShowCreationThenFadeOut(Succession):
    def __init__(self, mobject: Mobject, remover: bool = True, **kwargs):
        super().__init__(
            ShowCreation(mobject),
            FadeOut(mobject),
            remover=remover,
            **kwargs
        )


class AnimationOnSurroundingRectangle(AnimationGroup):
    RectAnimationType: type = Animation

    def __init__(
        self,
        mobject: Mobject,
        stroke_width: float = 2.0,
        stroke_color: ManimColor = YELLOW,
        buff: float = SMALL_BUFF,
        **kwargs
    ):
        rect = SurroundingRectangle(
            mobject,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            buff=buff,
        )
        rect.add_updater(lambda r: r.move_to(mobject))
        super().__init__(self.RectAnimationType(rect, **kwargs))


class ShowPassingFlashAround(AnimationOnSurroundingRectangle):
    RectAnimationType = ShowPassingFlash


class ShowCreationThenDestructionAround(AnimationOnSurroundingRectangle):
    RectAnimationType = ShowCreationThenDestruction


class ShowCreationThenFadeAround(AnimationOnSurroundingRectangle):
    RectAnimationType = ShowCreationThenFadeOut


class ApplyWave(Homotopy):
    def __init__(
        self,
        mobject: Mobject,
        direction: np.ndarray = UP,
        amplitude: float = 0.2,
        run_time: float = 1.0,
        **kwargs
    ):

        left_x = mobject.get_left()[0]
        right_x = mobject.get_right()[0]
        vect = amplitude * direction

        def homotopy(x, y, z, t):
            alpha = (x - left_x) / (right_x - left_x)
            power = np.exp(2.0 * (alpha - 0.5))
            nudge = there_and_back(t**power)
            return np.array([x, y, z]) + nudge * vect

        super().__init__(homotopy, mobject, **kwargs)


class WiggleOutThenIn(Animation):
    def __init__(
        self,
        mobject: Mobject,
        scale_value: float = 1.1,
        rotation_angle: float = 0.01 * TAU,
        n_wiggles: int = 6,
        scale_about_point: np.ndarray | None = None,
        rotate_about_point: np.ndarray | None = None,
        run_time: float = 2,
        **kwargs
    ):
        self.scale_value = scale_value
        self.rotation_angle = rotation_angle
        self.n_wiggles = n_wiggles
        self.scale_about_point = scale_about_point
        self.rotate_about_point = rotate_about_point
        super().__init__(mobject, run_time=run_time, **kwargs)

    def get_scale_about_point(self) -> np.ndarray:
        return self.scale_about_point or self.mobject.get_center()

    def get_rotate_about_point(self) -> np.ndarray:
        return self.rotate_about_point or self.mobject.get_center()

    def interpolate_submobject(
        self,
        submobject: Mobject,
        starting_sumobject: Mobject,
        alpha: float
    ) -> None:
        submobject.match_points(starting_sumobject)
        submobject.scale(
            interpolate(1, self.scale_value, there_and_back(alpha)),
            about_point=self.get_scale_about_point()
        )
        submobject.rotate(
            wiggle(alpha, self.n_wiggles) * self.rotation_angle,
            about_point=self.get_rotate_about_point()
        )


class TurnInsideOut(Transform):
    def __init__(self, mobject: Mobject, path_arc: float = 90 * DEG, **kwargs):
        super().__init__(mobject, path_arc=path_arc, **kwargs)

    def create_target(self) -> Mobject:
        result = self.mobject.copy().reverse_points()
        if isinstance(result, VMobject):
            result.refresh_triangulation()
        return result


class FlashyFadeIn(AnimationGroup):
    def __init__(self,
        vmobject: VMobject,
        stroke_width: float = 2.0,
        fade_lag: float = 0.0,
        time_width: float = 1.0,
        **kwargs
    ):
        outline = vmobject.copy()
        outline.set_fill(opacity=0)
        outline.set_stroke(width=stroke_width, opacity=1)

        rate_func = kwargs.get("rate_func", smooth)
        super().__init__(
            FadeIn(vmobject, rate_func=squish_rate_func(rate_func, fade_lag, 1)),
            VShowPassingFlash(outline, time_width=time_width),
            **kwargs
        )
