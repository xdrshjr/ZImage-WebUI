"""
API接口测试文件
测试所有API接口是否正常工作
"""
import argparse
import sys
import time
import requests
from pathlib import Path
from typing import Optional


class APITester:
    """API测试类"""
    
    def __init__(self, base_url: str):
        """
        初始化测试器
        
        Args:
            base_url: API基础URL，例如: http://localhost:5000
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """
        记录测试结果
        
        Args:
            test_name: 测试名称
            success: 是否成功
            message: 额外消息
        """
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "name": test_name,
            "success": success,
            "message": message
        }
        self.test_results.append(result)
        print(f"{status} - {test_name}")
        if message:
            print(f"    {message}")
    
    def test_health_check(self) -> bool:
        """
        测试健康检查接口
        
        Returns:
            bool: 测试是否通过
        """
        try:
            url = f"{self.base_url}/health"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                self.log_test("健康检查", False, f"状态码错误: {response.status_code}")
                return False
            
            data = response.json()
            if data.get("code") != 200:
                self.log_test("健康检查", False, f"返回码错误: {data.get('code')}")
                return False
            
            health_data = data.get("data", {})
            model_loaded = health_data.get("model_loaded", False)
            
            self.log_test(
                "健康检查",
                True,
                f"服务状态: {health_data.get('status')}, 模型已加载: {model_loaded}"
            )
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("健康检查", False, f"请求异常: {str(e)}")
            return False
        except Exception as e:
            self.log_test("健康检查", False, f"未知错误: {str(e)}")
            return False
    
    def test_generate_task(self, prompt: str = None) -> Optional[str]:
        """
        测试提交生成任务接口
        
        Args:
            prompt: 提示词，如果为None则使用默认值
            
        Returns:
            str: 任务ID，如果失败返回None
        """
        try:
            if prompt is None:
                prompt = "A beautiful sunset over the ocean, high quality, detailed"
            
            url = f"{self.base_url}/api/generate"
            data = {
                "prompt": prompt,
                "height": 1024,
                "width": 1024,
                "num_inference_steps": 9,
                "seed": 42
            }
            
            response = self.session.post(url, json=data, timeout=30)
            
            if response.status_code != 200:
                self.log_test(
                    "提交生成任务",
                    False,
                    f"状态码错误: {response.status_code}, 响应: {response.text[:200]}"
                )
                return None
            
            result = response.json()
            if result.get("code") != 200:
                self.log_test(
                    "提交生成任务",
                    False,
                    f"返回码错误: {result.get('code')}, 消息: {result.get('message')}"
                )
                return None
            
            task_data = result.get("data", {})
            task_id = task_data.get("task_id")
            
            if not task_id:
                self.log_test("提交生成任务", False, "未返回任务ID")
                return None
            
            status = task_data.get("status")
            queue_position = task_data.get("queue_position", 0)
            
            self.log_test(
                "提交生成任务",
                True,
                f"任务ID: {task_id}, 状态: {status}, 队列位置: {queue_position}"
            )
            return task_id
            
        except requests.exceptions.RequestException as e:
            self.log_test("提交生成任务", False, f"请求异常: {str(e)}")
            return None
        except Exception as e:
            self.log_test("提交生成任务", False, f"未知错误: {str(e)}")
            return None
    
    def test_get_task_status(self, task_id: str) -> bool:
        """
        测试查询任务状态接口
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 测试是否通过
        """
        try:
            url = f"{self.base_url}/api/task/{task_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                self.log_test(
                    "查询任务状态",
                    False,
                    f"状态码错误: {response.status_code}"
                )
                return False
            
            result = response.json()
            if result.get("code") != 200:
                self.log_test(
                    "查询任务状态",
                    False,
                    f"返回码错误: {result.get('code')}, 消息: {result.get('message')}"
                )
                return False
            
            task_data = result.get("data", {})
            status = task_data.get("status")
            prompt = task_data.get("prompt", "")[:50]
            
            self.log_test(
                "查询任务状态",
                True,
                f"任务状态: {status}, 提示词: {prompt}..."
            )
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("查询任务状态", False, f"请求异常: {str(e)}")
            return False
        except Exception as e:
            self.log_test("查询任务状态", False, f"未知错误: {str(e)}")
            return False
    
    def test_get_task_result(self, task_id: str, wait_for_completion: bool = True, max_wait_time: int = 300) -> bool:
        """
        测试获取任务结果接口
        
        Args:
            task_id: 任务ID
            wait_for_completion: 是否等待任务完成
            max_wait_time: 最大等待时间（秒）
            
        Returns:
            bool: 测试是否通过
        """
        try:
            # 如果等待完成，先轮询任务状态
            if wait_for_completion:
                print(f"    等待任务完成 (最多等待 {max_wait_time} 秒)...")
                start_time = time.time()
                
                while time.time() - start_time < max_wait_time:
                    url = f"{self.base_url}/api/task/{task_id}"
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        task_data = result.get("data", {})
                        status = task_data.get("status")
                        
                        if status == "completed":
                            print(f"    任务已完成，耗时: {int(time.time() - start_time)} 秒")
                            break
                        elif status == "failed":
                            error_msg = task_data.get("error_message", "未知错误")
                            self.log_test(
                                "获取任务结果",
                                False,
                                f"任务失败: {error_msg}"
                            )
                            return False
                        else:
                            print(f"    当前状态: {status}, 等待中...")
                            time.sleep(2)
                    else:
                        time.sleep(2)
                else:
                    self.log_test(
                        "获取任务结果",
                        False,
                        f"任务超时，超过 {max_wait_time} 秒未完成"
                    )
                    return False
            
            # 获取结果
            url = f"{self.base_url}/api/result/{task_id}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code != 200:
                self.log_test(
                    "获取任务结果",
                    False,
                    f"状态码错误: {response.status_code}"
                )
                return False
            
            # 检查是否是图像文件
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type:
                # 保存图像文件
                output_dir = Path("tests/output")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"test_result_{task_id}.png"
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content) / 1024  # KB
                self.log_test(
                    "获取任务结果",
                    True,
                    f"图像已保存: {output_path}, 大小: {file_size:.2f} KB"
                )
                return True
            else:
                # 可能是JSON响应（任务未完成）
                try:
                    result = response.json()
                    status = result.get("data", {}).get("status", "unknown")
                    self.log_test(
                        "获取任务结果",
                        False,
                        f"任务未完成，状态: {status}"
                    )
                    return False
                except:
                    self.log_test(
                        "获取任务结果",
                        False,
                        f"响应格式错误，Content-Type: {content_type}"
                    )
                    return False
                    
        except requests.exceptions.RequestException as e:
            self.log_test("获取任务结果", False, f"请求异常: {str(e)}")
            return False
        except Exception as e:
            self.log_test("获取任务结果", False, f"未知错误: {str(e)}")
            return False
    
    def test_get_system_status(self) -> bool:
        """
        测试查询系统状态接口
        
        Returns:
            bool: 测试是否通过
        """
        try:
            url = f"{self.base_url}/api/status"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                self.log_test(
                    "查询系统状态",
                    False,
                    f"状态码错误: {response.status_code}"
                )
                return False
            
            result = response.json()
            if result.get("code") != 200:
                self.log_test(
                    "查询系统状态",
                    False,
                    f"返回码错误: {result.get('code')}"
                )
                return False
            
            status_data = result.get("data", {})
            queue_info = status_data.get("queue", {})
            gpu_info = status_data.get("gpu", {})
            model_loaded = status_data.get("model_loaded", False)
            
            queue_size = queue_info.get("queue_size", 0)
            gpu_available = gpu_info.get("available", False)
            gpu_usage = gpu_info.get("memory_usage_percent", 0)
            
            message = (
                f"队列长度: {queue_size}, "
                f"模型已加载: {model_loaded}, "
                f"GPU可用: {gpu_available}"
            )
            if gpu_available:
                message += f", GPU使用率: {gpu_usage}%"
            
            self.log_test("查询系统状态", True, message)
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("查询系统状态", False, f"请求异常: {str(e)}")
            return False
        except Exception as e:
            self.log_test("查询系统状态", False, f"未知错误: {str(e)}")
            return False
    
    def test_invalid_parameters(self) -> bool:
        """
        测试参数验证
        
        Returns:
            bool: 测试是否通过
        """
        try:
            url = f"{self.base_url}/api/generate"
            
            # 测试缺少prompt参数
            response = self.session.post(url, json={}, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 400:
                    self.log_test("参数验证 - 缺少prompt", True, "正确返回400错误")
                else:
                    self.log_test(
                        "参数验证 - 缺少prompt",
                        False,
                        f"应该返回400，实际返回: {result.get('code')}"
                    )
                    return False
            else:
                self.log_test(
                    "参数验证 - 缺少prompt",
                    False,
                    f"状态码错误: {response.status_code}"
                )
                return False
            
            # 测试无效的height参数
            response = self.session.post(
                url,
                json={"prompt": "test", "height": -1},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 400:
                    self.log_test("参数验证 - 无效height", True, "正确返回400错误")
                else:
                    self.log_test(
                        "参数验证 - 无效height",
                        False,
                        f"应该返回400，实际返回: {result.get('code')}"
                    )
                    return False
            
            # 测试不存在的任务ID
            fake_task_id = "00000000-0000-0000-0000-000000000000"
            response = self.session.get(
                f"{self.base_url}/api/task/{fake_task_id}",
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 404:
                    self.log_test("参数验证 - 不存在任务", True, "正确返回404错误")
                else:
                    self.log_test(
                        "参数验证 - 不存在任务",
                        False,
                        f"应该返回404，实际返回: {result.get('code')}"
                    )
                    return False
            
            return True
            
        except Exception as e:
            self.log_test("参数验证", False, f"测试异常: {str(e)}")
            return False
    
    def run_all_tests(self, test_image_generation: bool = True, wait_for_completion: bool = True):
        """
        运行所有测试
        
        Args:
            test_image_generation: 是否测试图像生成（需要等待较长时间）
            wait_for_completion: 是否等待图像生成完成
        """
        print("=" * 60)
        print("开始API接口测试")
        print(f"测试目标: {self.base_url}")
        print("=" * 60)
        print()
        
        # 1. 健康检查
        print("【1/6】测试健康检查接口...")
        health_ok = self.test_health_check()
        print()
        
        if not health_ok:
            print("❌ 健康检查失败，服务可能未启动或不可用")
            print("请确保服务已启动并可以访问")
            return
        
        # 2. 查询系统状态
        print("【2/6】测试查询系统状态接口...")
        self.test_get_system_status()
        print()
        
        # 3. 参数验证
        print("【3/6】测试参数验证...")
        self.test_invalid_parameters()
        print()
        
        # 4. 提交生成任务
        print("【4/6】测试提交生成任务接口...")
        task_id = self.test_generate_task()
        print()
        
        if not task_id:
            print("❌ 提交任务失败，跳过后续测试")
            return
        
        # 5. 查询任务状态
        print("【5/6】测试查询任务状态接口...")
        self.test_get_task_status(task_id)
        print()
        
        # 6. 获取任务结果（如果启用）
        if test_image_generation:
            print("【6/6】测试获取任务结果接口...")
            self.test_get_task_result(task_id, wait_for_completion=wait_for_completion)
            print()
        else:
            print("【6/6】跳过图像生成测试（使用 --skip-image-generation）")
            print()
        
        # 打印测试总结
        print("=" * 60)
        print("测试总结")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print()
        
        if failed_tests > 0:
            print("失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['name']}: {result['message']}")
        
        print("=" * 60)
        
        # 返回退出码
        return 0 if failed_tests == 0 else 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Z-Image-Turbo API接口测试工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 测试本地服务（默认）
  python tests/test_api.py
  
  # 测试指定IP和端口
  python tests/test_api.py --host 192.168.1.100 --port 8080
  
  # 测试但不等待图像生成完成
  python tests/test_api.py --skip-image-generation
  
  # 测试但跳过图像生成相关测试
  python tests/test_api.py --skip-image-generation --no-wait
        """
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='192.168.1.114',
        help='服务器IP地址 (默认: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='服务器端口 (默认: 5000)'
    )
    
    parser.add_argument(
        '--skip-image-generation',
        action='store_true',
        help='跳过图像生成测试（不等待图像生成完成）'
    )
    
    parser.add_argument(
        '--no-wait',
        action='store_true',
        help='不等待任务完成（仅查询状态，不下载图像）'
    )
    
    args = parser.parse_args()
    
    # 构建基础URL
    base_url = f"http://{args.host}:{args.port}"
    
    # 创建测试器
    tester = APITester(base_url)
    
    # 运行测试
    test_image = not args.skip_image_generation
    wait_completion = not args.no_wait
    
    exit_code = tester.run_all_tests(
        test_image_generation=test_image,
        wait_for_completion=wait_completion
    )
    
    sys.exit(exit_code if exit_code is not None else 0)


if __name__ == "__main__":
    main()


