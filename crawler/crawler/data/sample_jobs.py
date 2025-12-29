import json
import os

def sample_jobs_by_interval(input_file: str, output_file: str, interval: int = 100):
    """
    从输入JSON文件中按指定间隔抽取数据，保存到新的JSON文件
    
    Args:
        input_file: 输入JSON文件路径
        output_file: 输出JSON文件路径
        interval: 抽取间隔（每interval条选1条）
    """
    # 校验输入文件是否存在
    if not os.path.exists(input_file):
        raise FileExistsError(f"输入文件{input_file}不存在")
    
    # 读取并解析输入JSON文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON解析失败：{e}")
    except PermissionError:
        raise PermissionError(f"无权限读取文件{input_file}")
    
    # 校验数据格式是否为列表
    if not isinstance(data, list):
        raise TypeError("请输入JSON文件的根目录必须是列表")
    
    # 校验列表元素是否为字典
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise TypeError(f"第{idx}条数据不是字典格式：{item}")
        
    # 按间隔抽取数据（每interval条选一条，从0开始计数）
    sampled_data = []
    for idx in range(0, len(data), interval):
        sampled_data.append(data[idx])
    
    # 写入输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # indent=2 格式化输出，便于阅读
            json.dump(sampled_data, f, ensure_ascii=False, indent=2)
        print(f"抽取完成！")
        print(f"原始数据总数：{len(data)}")
        print(f"抽取数据总数：{len(sampled_data)}")
        print(f"结果已保存至：{output_file}")
    except PermissionError:
        raise PermissionError(f"无权限写入文件 {output_file}")
    except Exception as e:
        raise Exception(f"写入文件失败：{e}")
if __name__ == "__main__":
    # 配置文件路径
    INPUT_FILE = "jobs.json"
    OUTPUT_FILE = "sampled_jobs.json"
    SAMPLE_INTERVAL = 1800 # 每1800条选1条

    try:
        sample_jobs_by_interval(INPUT_FILE, OUTPUT_FILE, SAMPLE_INTERVAL)
    except Exception as e:
        print(f"执行失败：{e}")