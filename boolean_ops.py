# 从__future__导入annotations以支持类型注解的前向引用
from __future__ import annotations

import numpy as np
import pathops  # 导入路径运算库，用于处理图形布尔运算
from manimlib.mobject.types.vectorized_mobject import VMobject  # 导入Manim的向量图形基类


# 2D图形对象(VMobject)之间的布尔运算实现
# 代码借鉴自：https://github.com/ManimCommunity/manim/


def _convert_vmobject_to_skia_path(vmobject: VMobject) -> pathops.Path:
    """
    将Manim的向量图形对象(VMobject)转换为pathops库可处理的Path对象
    
    布尔运算依赖pathops库，因此需要先将Manim的图形格式转换为该库支持的路径格式。
    转换过程会保留图形的路径信息（如贝塞尔曲线、闭合状态等）。
    
    参数:
        vmobject: 待转换的Manim向量图形对象
        
    返回:
        pathops.Path: 转换后的路径对象，可用于pathops的布尔运算
    """
    # 创建一个空的pathops路径对象，用于存储转换结果
    path = pathops.Path()
    
    # 遍历当前图形及其所有子图形（family_members_with_points()返回包含顶点数据的所有成员）
    for submob in vmobject.family_members_with_points():
        # 遍历子图形中的每一条子路径（一个复杂图形可能由多个子路径组成）
        for subpath in submob.get_subpaths():
            # 将子路径的顶点数据转换为贝塞尔曲线元组（p0起点, p1控制点, p2终点）
            quads = vmobject.get_bezier_tuples_from_points(subpath)
            
            # 获取子路径的起始点（取前2个坐标，忽略z轴，因为布尔运算为2D操作）
            start = subpath[0]
            path.moveTo(*start[:2])  # 将路径移动到起始点
            
            # 遍历所有贝塞尔曲线段，添加到pathops路径中
            for p0, p1, p2 in quads:
                # 添加二次贝塞尔曲线：p1为控制点，p2为终点
                path.quadTo(*p1[:2], *p2[:2])
            
            # 检查路径是否闭合（起点与终点是否相同）
            if vmobject.consider_points_equal(subpath[0], subpath[-1]):
                path.close()  # 闭合路径
    
    return path


def _convert_skia_path_to_vmobject(
    path: pathops.Path,
    vmobject: VMobject
) -> VMobject:
    """
    将pathops运算后的Path对象转换回Manim的VMobject对象
    
    布尔运算的结果是pathops.Path格式，需要转换回Manim可渲染的VMobject格式，
    才能在动画中显示。转换过程会还原路径的线条、曲线和闭合状态。
    
    参数:
        path: 布尔运算后的pathops路径对象
        vmobject: 用于存储转换结果的VMobject实例（空对象）
        
    返回:
        VMobject: 转换后的Manim向量图形对象
    """
    # 获取pathops中的路径操作枚举（如移动、画线、贝塞尔曲线、闭合等）
    PathVerb = pathops.PathVerb
    # 记录当前路径的起点（用于闭合路径时返回起点），初始化为3D坐标（z轴为0，适配Manim的3D系统）
    current_path_start = np.array([0.0, 0.0, 0.0])
    
    # 遍历pathops路径中的每一个操作（路径动词+对应坐标点）
    for path_verb, points in path:
        if path_verb == PathVerb.CLOSE:
            # 处理闭合路径：添加一条从当前点到起点的线段
            vmobject.add_line_to(current_path_start)
        else:
            # 将pathops的2D点坐标(x,y)扩展为3D坐标(x,y,0)，适配Manim的3D坐标系统
            points = np.hstack((np.array(points), np.zeros((len(points), 1))))
            
            if path_verb == PathVerb.MOVE:
                # 处理"移动"操作：移动到新起点并开始新路径
                for point in points:
                    current_path_start = point  # 更新当前路径起点
                    vmobject.start_new_path(point)  # 启动新路径
            
            elif path_verb == PathVerb.CUBIC:
                # 处理三次贝塞尔曲线：添加三次贝塞尔线段（需2个控制点+1个终点）
                vmobject.add_cubic_bezier_curve_to(*points)
            
            elif path_verb == PathVerb.LINE:
                # 处理直线：添加从当前点到目标点的线段
                vmobject.add_line_to(points[0])
            
            elif path_verb == PathVerb.QUAD:
                # 处理二次贝塞尔曲线：添加二次贝塞尔线段（需1个控制点+1个终点）
                vmobject.add_quadratic_bezier_curve_to(*points)
            
            else:
                # 抛出异常处理不支持的路径操作
                raise Exception(f"不支持的路径操作: {path_verb}")
    
    # 反转点的顺序（适配Manim内部的路径渲染逻辑）并返回结果
    return vmobject.reverse_points()


class Union(VMobject):
    """
    实现多个向量图形(VMobject)的并集布尔运算
    
    并集结果为：包含所有输入图形的区域（合并重叠部分，保留所有图形的非重叠部分）。
    例如，两个圆形的并集是一个包含两个圆全部区域的图形。
    """
    def __init__(self, *vmobjects: VMobject, **kwargs):
        """
        初始化并集对象，计算多个图形的并集
        
        参数:
            *vmobjects: 待合并的多个向量图形（至少需要2个）
            **kwargs: 传递给父类VMobject的关键字参数（如颜色、填充等样式属性）
        """
        # 检查输入合法性：并集运算至少需要2个图形
        if len(vmobjects) < 2:
            raise ValueError("Union运算至少需要2个图形对象。")
        # 调用父类构造函数，初始化图形的基础属性
        super().__init__(** kwargs)
        
        # 创建空的pathops路径对象，用于存储并集运算结果
        outpen = pathops.Path()
        # 将所有输入图形转换为pathops路径格式
        paths = [
            _convert_vmobject_to_skia_path(vmobject)
            for vmobject in vmobjects
        ]
        
        # 执行并集运算：合并所有路径为一个整体
        pathops.union(paths, outpen.getPen())
        # 将运算结果转换回VMobject，存储到当前实例中
        _convert_skia_path_to_vmobject(outpen, self)


class Difference(VMobject):
    """
    实现两个向量图形(VMobject)的差集布尔运算
    
    差集结果为：保留第一个图形（主体）中未被第二个图形（裁剪）覆盖的区域。
    例如，圆形A减去圆形B的差集是A中不与B重叠的部分。
    """
    def __init__(self, subject: VMobject, clip: VMobject, **kwargs):
        """
        初始化差集对象，计算两个图形的差集
        
        参数:
            subject: 被减的主体图形（保留其未被裁剪的部分）
            clip: 用于裁剪的图形（移除主体中与它重叠的部分）
            **kwargs: 传递给父类VMobject的关键字参数
        """
        # 调用父类构造函数，初始化基础属性
        super().__init__(** kwargs)
        
        # 创建空的pathops路径对象，用于存储差集运算结果
        outpen = pathops.Path()
        # 执行差集运算：主体图形 - 裁剪图形
        pathops.difference(
            [_convert_vmobject_to_skia_path(subject)],  # 主体图形的路径列表
            [_convert_vmobject_to_skia_path(clip)],     # 裁剪图形的路径列表
            outpen.getPen(),                            # 存储结果的画笔
        )
        
        # 将运算结果转换回VMobject
        _convert_skia_path_to_vmobject(outpen, self)


class Intersection(VMobject):
    """
    实现多个向量图形(VMobject)的交集布尔运算
    
    交集结果为：所有输入图形共同重叠的区域（仅保留同时被所有图形覆盖的部分）。
    例如，三个圆形的交集是同时位于三个圆内的区域。
    """
    def __init__(self, *vmobjects: VMobject, **kwargs):
        """
        初始化交集对象，计算多个图形的交集
        
        参数:
            *vmobjects: 待计算交集的多个图形（至少需要2个）
            **kwargs: 传递给父类VMobject的关键字参数
        """
        # 检查输入合法性：交集运算至少需要2个图形
        if len(vmobjects) < 2:
            raise ValueError("Intersection运算至少需要2个图形对象。")
        # 调用父类构造函数，初始化基础属性
        super().__init__(** kwargs)
        
        # 创建空的pathops路径对象，用于存储运算结果
        outpen = pathops.Path()
        # 先计算前两个图形的交集
        pathops.intersection(
            [_convert_vmobject_to_skia_path(vmobjects[0])],  # 第一个图形路径
            [_convert_vmobject_to_skia_path(vmobjects[1])],  # 第二个图形路径
            outpen.getPen(),                                 # 存储结果
        )
        
        # 若有更多图形，依次与当前交集结果求新交集（迭代计算总交集）
        new_outpen = outpen  # 临时变量存储每次迭代的新结果
        for _i in range(2, len(vmobjects)):
            new_outpen = pathops.Path()  # 重置临时路径
            # 用当前交集结果与下一个图形计算新交集
            pathops.intersection(
                [outpen],  # 上一次的交集结果
                [_convert_vmobject_to_skia_path(vmobjects[_i])],  # 下一个图形路径
                new_outpen.getPen(),  # 存储新结果
            )
            outpen = new_outpen  # 更新交集结果
        
        # 将最终交集结果转换回VMobject
        _convert_skia_path_to_vmobject(outpen, self)


class Exclusion(VMobject):
    """
    实现多个向量图形(VMobject)的异或（对称差）布尔运算
    
    异或结果为：所有图形中仅被单个图形覆盖的区域（排除所有重叠部分）。
    例如，两个圆形的异或是"仅在A中"或"仅在B中"的区域，不包括重叠部分。
    """
    def __init__(self, *vmobjects: VMobject, **kwargs):
        """
        初始化异或对象，计算多个图形的异或结果
        
        参数:
            *vmobjects: 待计算异或的多个图形（至少需要2个）
            **kwargs: 传递给父类VMobject的关键字参数
        """
        # 检查输入合法性：异或运算至少需要2个图形
        if len(vmobjects) < 2:
            raise ValueError("Exclusion运算至少需要2个图形对象。")
        # 调用父类构造函数，初始化基础属性
        super().__init__(** kwargs)
        
        # 创建空的pathops路径对象，用于存储运算结果
        outpen = pathops.Path()
        # 先计算前两个图形的异或
        pathops.xor(
            [_convert_vmobject_to_skia_path(vmobjects[0])],  # 第一个图形路径
            [_convert_vmobject_to_skia_path(vmobjects[1])],  # 第二个图形路径
            outpen.getPen(),                                 # 存储结果
        )
        
        # 若有更多图形，依次与当前异或结果求新异或（迭代计算总异或）
        new_outpen = outpen  # 临时变量存储每次迭代的新结果
        for _i in range(2, len(vmobjects)):
            new_outpen = pathops.Path()  # 重置临时路径
            # 用当前异或结果与下一个图形计算新异或
            pathops.xor(
                [outpen],  # 上一次的异或结果
                [_convert_vmobject_to_skia_path(vmobjects[_i])],  # 下一个图形路径
                new_outpen.getPen(),  # 存储新结果
            )
            outpen = new_outpen  # 更新异或结果
        
        # 将最终异或结果转换回VMobject
        _convert_skia_path_to_vmobject(outpen, self)