from  base.utils import *
@singleton
class MyClass:
    def __init__(self, value):
        self.value = value

# 创建两个实例
instance1 = MyClass(10)
instance2 = MyClass(20)

# 检查两个实例是否是同一个对象
print(instance1 is instance2)  # 应该输出 True
print(instance1.value)  # 应该输出 10
print(instance2.value)  # 应该输出 10，因为 instance2 实际上是 instance1
