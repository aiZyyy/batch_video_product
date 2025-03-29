import os
import yaml
from datetime import datetime
from gradio_client import Client, handle_file


class VideoGenerator:
    def __init__(self, config_path="config.yaml"):
        self.load_config(config_path)
        self.client = Client(self.config["api_config"]["endpoint"])
        self.setup_directories()

    def load_config(self, config_path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def setup_directories(self):
        os.makedirs(self.config["paths"]["output_dir"], exist_ok=True)
        os.makedirs(self.config["paths"]["log_dir"], exist_ok=True)

    def validate_file(self, file_path, allowed_types):
        # 文件校验逻辑
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in allowed_types:
            raise ValueError(f"不支持的文件类型 {ext}")
        return True

    def process_video(self, video_path, audio_path):
        # 文件校验
        self.validate_file(
            video_path, self.config["file_settings"]["allowed_video_types"]
        )
        self.validate_file(
            audio_path, self.config["file_settings"]["allowed_audio_types"]
        )

        # 构造请求参数
        video_data = {"video": handle_file(video_path)}
        audio_data = handle_file(audio_path)

        # 调用API
        result = self.client.predict(
            video=video_data,
            audio=audio_data,
            api_name=self.config["api_config"]["api_name"],
        )
        # 结构诊断
        self.validate_output_structure(result)

        # 处理结果
        output_video = result[0]["video"]["path"]
        processing_time = result[1]

        # 在 process_video 方法中添加诊断代码
        print("原始返回类型:", type(result))
        print("返回结构转字符串:", str(result)[:500])  # 防止超长输出

        # 移动输出文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"output_{timestamp}{os.path.splitext(output_video)[1]}"
        final_path = os.path.join(self.config["paths"]["output_dir"], output_filename)
        os.rename(output_video, final_path)

        # 记录日志
        self.log_processing(processing_time, final_path)

        return final_path, processing_time

    def log_processing(self, time_str, file_path):
        log_entry = f"{datetime.now()}\t生成文件：{file_path}\t耗时：{time_str}\n"
        log_file = os.path.join(self.config["paths"]["log_dir"], "processing.log")
        with open(log_file, "a") as f:
            f.write(log_entry)

    # 在类中添加类型检查方法


def validate_output_structure(self, data):
    """验证API返回数据结构"""
    if isinstance(data, (list, tuple)):
        return {"type": "tuple/list", "length": len(data), "sample": str(data)[:200]}
    elif isinstance(data, dict):
        return {"type": "dict", "keys": list(data.keys()), "sample": str(data)[:200]}
    else:
        return {"type": type(data), "sample": str(data)}


# 在 process_video 方法中调用
structure_report = self.validate_output_structure(result)
print("API返回结构诊断报告:\n", json.dumps(structure_report, indent=2))


if __name__ == "__main__":
    generator = VideoGenerator()

    # 示例使用（实际应从配置文件读取路径）
    video_path = "./inputs/video/video1.mp4"
    audio_path = "./inputs/audio/audio1.wav"

    try:
        result_path, time_cost = generator.process_video(video_path, audio_path)
        print(f"视频生成成功！保存路径：{result_path}\n生成耗时：{time_cost}")
    except Exception as e:
        print(f"处理失败：{str(e)}")
