# 启用Python 3.7+的注解向前兼容支持，允许在类型注解中使用尚未定义的类
from __future__ import annotations

# 从Manim的变换动画模块导入Transform类，用于对象间的变换动画
from manimlib.animation.transform import Transform

# 导入类型检查相关模块
from typing import TYPE_CHECKING

# 条件导入，仅在类型检查时执行（运行时不生效）
# 用于解决循环导入问题，同时提供完整的类型提示支持
if TYPE_CHECKING:
    import numpy as np  # 导入numpy库，用于数值计算相关的类型提示
    
    from manimlib.mobject.geometry import Arrow  # 导入箭头图形类Arrow
    from manimlib.mobject.mobject import Mobject  # 导入基础可移动对象类Mobject
    from manimlib.typing import ManimColor  # 导入Manim颜色类型ManimColor


class GrowFromPoint(Transform):
    def __init__(
        self,
        mobject: Mobject,
        point: np.ndarray,
        point_color: ManimColor = None,
        **kwargs
    ):
        self.point = point
        self.point_color = point_color
        super().__init__(mobject, **kwargs)

    def create_target(self) -> Mobject:
        return self.mobject.copy()

    def create_starting_mobject(self) -> Mobject:
        start = super().create_starting_mobject()
        start.scale(0)
        start.move_to(self.point)
        if self.point_color is not None:
            start.set_color(self.point_color)
        return start


class GrowFromCenter(GrowFromPoint):
    def __init__(self, mobject: Mobject, **kwargs):
        point = mobject.get_center()
        super().__init__(mobject, point, **kwargs)


class GrowFromEdge(GrowFromPoint):
    def __init__(self, mobject: Mobject, edge: np.ndarray, **kwargs):
        point = mobject.get_bounding_box_point(edge)
        super().__init__(mobject, point, **kwargs)


class GrowArrow(GrowFromPoint):
    def __init__(self, arrow: Arrow, **kwargs):
        point = arrow.get_start()
        super().__init__(arrow, point, **kwargs)
