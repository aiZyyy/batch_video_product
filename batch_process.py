import json
import os
from gradio_client import Client, handle_file
from datetime import datetime

# ---------------------------
# 配置读取与初始化
# ---------------------------
# 读取配置文件
with open("config.json", "r") as f:
    config = json.load(f)

# 创建输出目录
os.makedirs(config["output_dir"], exist_ok=True)

# 初始化客户端
client = Client("http://127.0.0.1:7861/")

# ---------------------------
# 批量处理函数
# ---------------------------
def process_video_audio(video_path, audio_path, output_dir):
    """处理单个视频-音频对"""
    try:
        # 步骤1: 降低分辨率
        print(f"\n处理视频: {os.path.basename(video_path)}")
        trans_result = client.predict(
            input_video={"video": handle_file(video_path)},
            height=config["trans_low_config"]["height"],
            api_name="/trans_low"
        )
        low_res_path = trans_result["video"]["path"]

        # 步骤2: 生成数字人视频
        do_make_result = client.predict(
            video={"video": handle_file(low_res_path)},
            audio=handle_file(audio_path),
            api_name="/do_make"
        )
        generated_video = do_make_result[0]["video"]["path"]
        processing_time = do_make_result[1]

        # 保存结果（可自定义文件名规则）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"result_{timestamp}.mp4"
        output_path = os.path.join(output_dir, output_name)
        os.rename(generated_video, output_path)  # 移动文件到输出目录

        return {
            "status": "success",
            "input_video": video_path,
            "input_audio": audio_path,
            "output_path": output_path,
            "processing_time": processing_time
        }
    except Exception as e:
        return {
            "status": "failed",
            "input_video": video_path,
            "input_audio": audio_path,
            "error": str(e)
        }

# ---------------------------
# 主循环逻辑
# ---------------------------
results = []

# 遍历所有视频与音频组合（这里演示全组合配对，按需修改）
for video_idx, video_path in enumerate(config["video_paths"]):
    for audio_idx, audio_path in enumerate(config["audio_paths"]):
        result = process_video_audio(video_path, audio_path, config["output_dir"])
        results.append(result)
        print(f"进度: 视频 {video_idx+1}/{len(config['video_paths'])} | 音频 {audio_idx+1}/{len(config['audio_paths'])}")

# ---------------------------
# 保存处理日志
# ---------------------------
log_path = os.path.join(config["output_dir"], "process_log.json")
with open(log_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n处理完成！日志已保存至 {log_path}")