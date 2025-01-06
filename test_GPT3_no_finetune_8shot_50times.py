import openai
from tqdm import tqdm
import json
from extract_number import extract_last_number
import os

file_path = "data/test_messages.jsonl"
model_id = "gpt-3.5-turbo-0125"
api_key = os.getenv('OPENAI_API_KEY')

# 模型加载
client = openai.OpenAI(
    api_key=api_key
)

# 8-shot 示例
messages_8shot = [
    {"role": "system",
     "content": "As an expert problem solver, solve step by step the following mathematical questions."},

    {"role": "user",
     "content": "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"},
    {"role": "assistant",
     "content": "Let’s think step by step. Natalia sold 48/2 = <<48/2=24>>24 clips in May.\nNatalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May.\nThe final answer is 72"},

    {"role": "user",
     "content": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?"},
    {"role": "assistant",
     "content": "Let’s think step by step. Weng earns 12/60 = $<<12/60=0.2>>0.2 per minute.\nWorking 50 minutes, she earned 0.2 x 50 = $<<0.2*50=10>>10.\nThe final answer is 10"},

    {"role": "user",
     "content": "Betty is saving money for a new wallet which costs $100. Betty has only half of the money she needs. Her parents decided to give her $15 for that purpose, and her grandparents twice as much as her parents. How much more money does Betty need to buy the wallet?"},
    {"role": "assistant",
     "content": "Let’s think step by step. In the beginning, Betty has only 100 / 2 = $<<100/2=50>>50.\nBetty's grandparents gave her 15 * 2 = $<<15*2=30>>30.\nThis means, Betty needs 100 - 50 - 30 - 15 = $<<100-50-30-15=5>>5 more.\nThe final answer is 5"},

    {"role": "user",
     "content": "Julie is reading a 120-page book. Yesterday, she was able to read 12 pages and today, she read twice as many pages as yesterday. If she wants to read half of the remaining pages tomorrow, how many pages should she read?"},
    {"role": "assistant",
     "content": "Let’s think step by step. Julie read 12 x 2 = <<12*2=24>>24 pages today.\nSo she was able to read a total of 12 + 24 = <<12+24=36>>36 pages since yesterday.\nThere are 120 - 36 = <<120-36=84>>84 pages left to be read.\nSince she wants to read half of the remaining pages tomorrow, then she should read 84/2 = <<84/2=42>>42 pages.\nThe final answer is 42"},

    {"role": "user",
     "content": "James writes a 3-page letter to 2 different friends twice a week. How many pages does he write a year?"},
    {"role": "assistant",
     "content": "Let’s think step by step. He writes each friend 3*2=<<3*2=6>>6 pages a week.\nSo he writes 6*2=<<6*2=12>>12 pages every week.\nThat means he writes 12*52=<<12*52=624>>624 pages a year.\nThe final answer is 624"},

    {"role": "user",
     "content": "Mark has a garden with flowers. He planted plants of three different colors in it. Ten of them are yellow, and there are 80% more of those in purple. There are only 25% as many green flowers as there are yellow and purple flowers. How many flowers does Mark have in his garden?"},
    {"role": "assistant",
     "content": "Let’s think step by step. There are 80/100 * 10 = <<80/100*10=8>>8 more purple flowers than yellow flowers.\nSo in Mark's garden, there are 10 + 8 = <<10+8=18>>18 purple flowers.\nPurple and yellow flowers sum up to 10 + 18 = <<10+18=28>>28 flowers.\nThat means in Mark's garden there are 25/100 * 28 = <<25/100*28=7>>7 green flowers.\nSo in total Mark has 28 + 7 = <<28+7=35>>35 plants in his garden.\nThe final answer is 35"},

    {"role": "user",
     "content": "Albert is wondering how much pizza he can eat in one day. He buys 2 large pizzas and 2 small pizzas. A large pizza has 16 slices and a small pizza has 8 slices. If he eats it all, how many pieces does he eat that day?"},
    {"role": "assistant",
     "content": "Let’s think step by step. He eats 32 from the largest pizzas because 2 x 16 = <<2*16=32>>32.\nHe eats 16 from the small pizza because 2 x 8 = <<2*8=16>>16.\nHe eats 48 pieces because 32 + 16 = <<32+16=48>>48.\nThe final answer is 48"},

    {"role": "user",
     "content": "Ken created a care package to send to his brother, who was away at boarding school. Ken placed a box on a scale, and then he poured into the box enough jelly beans to bring the weight to 2 pounds. Then, he added enough brownies to cause the weight to triple. Next, he added another 2 pounds of jelly beans. And finally, he added enough gummy worms to double the weight once again. What was the final weight of the box of goodies, in pounds?"},
    {"role": "assistant",
     "content": "Let’s think step by step. To the initial 2 pounds of jelly beans, he added enough brownies to cause the weight to triple, bringing the weight to 2*3=<<2*3=6>>6 pounds.\nNext, he added another 2 pounds of jelly beans, bringing the weight to 6+2=<<6+2=8>>8 pounds.\nAnd finally, he added enough gummy worms to double the weight once again, to a final weight of 8*2=<<8*2=16>>16 pounds.\nThe final answer is 16"}
]

# 执行 50 次的准确率统计
results = []  # 用于存储每次执行的准确率
num_iterations = 50  # 总执行次数

for iteration in range(num_iterations):
    print(f"\nRunning iteration {iteration + 1}/{num_iterations}...")

    predict_right = 0  # 预测正确数
    test_examples = 0  # 样例数量
    skip_example = 0  # 跳过数量

    # 统计数据总量，用于初始化 tqdm
    with open(file_path, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)

    with open(file_path, mode='r', encoding='utf-8') as file, tqdm(total=total_lines, desc="Processing", unit="line") as pbar:
        for line in file:
            test_examples += 1
            if test_examples == 21:  # 只测试前 20 个样例
                test_examples -= 1
                break
            try:
                line = line.strip()

                # 尝试解析 JSON 行
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    skip_example += 1
                    test_examples -= 1
                    continue  # 跳过当前行

                # 获取问题和答案
                qn = data["messages"][1]["content"]  # 问题
                messages_8shot.append({"role": "user", "content": qn})
                answer = data["messages"][2]["content"]
                value = extract_last_number(answer)  # 正确答案

                # GPT 模型调用
                try:
                    completion = client.chat.completions.create(
                        model=model_id,
                        messages=messages_8shot,
                        temperature=0.2,
                        top_p=0.9
                    )
                except Exception as e:
                    skip_example += 1
                    test_examples -= 1
                    continue  # 跳过当前问题

                text = completion.choices[0].message.content
                predict_value = extract_last_number(text)  # 模型预测答案

                # 处理预测值为空的情况
                if predict_value is None:
                    predict_value = 0

                # 比较答案
                if abs(predict_value - value) < 0.0001:
                    predict_right += 1

            except Exception as e:
                test_examples -= 1
                skip_example += 1
                continue  # 跳过当前行

            # 更新进度条
            pbar.update(1)

    # 计算准确率
    accuracy = predict_right / test_examples if test_examples > 0 else 0
    print(f"Iteration {iteration + 1} Accuracy: {accuracy:.2%}")
    results.append({"iteration": iteration + 1, "accuracy": accuracy})

# 保存 50 次准确率结果到文件
output_file = "accuracy_GPT_no_finetune_8shot_50times.jsonl"
with open(output_file, "w", encoding="utf-8") as f:
    for result in results:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

print("\nResults saved to:", output_file)
