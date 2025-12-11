/**
 * LLM服务
 * 用于调用LLM进行提示词润色
 */

import axios, { AxiosInstance } from 'axios';
import { logger } from './logger';

interface LLMConfig {
  apiKey: string;
  apiUrl: string;
  model: string;
}

interface OpenAIResponse {
  choices: Array<{
    message: {
      content: string;
    };
  }>;
}

interface SimpleLLMResponse {
  content: string;
  error?: string;
}

type LLMResponse = OpenAIResponse | SimpleLLMResponse;

/**
 * 获取LLM配置
 * 从环境变量读取配置
 */
const getLLMConfig = (): LLMConfig | null => {
  const apiKey = process.env.NEXT_PUBLIC_LLM_API_KEY;
  const apiUrl = process.env.NEXT_PUBLIC_LLM_API_URL;
  const model = process.env.NEXT_PUBLIC_LLM_MODEL;

  if (!apiKey || !apiUrl || !model) {
    logger.warn('LLM配置不完整', {
      hasApiKey: !!apiKey,
      hasApiUrl: !!apiUrl,
      hasModel: !!model,
    });
    return null;
  }

  return { apiKey, apiUrl, model };
};

/**
 * 创建LLM API客户端
 */
const createLLMClient = (config: LLMConfig): AxiosInstance => {
  const client = axios.create({
    baseURL: config.apiUrl,
    timeout: 60000, // 60秒超时
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.apiKey}`,
    },
  });

  // 请求拦截器：记录请求日志
  client.interceptors.request.use(
    (config) => {
      logger.debug('LLM请求', {
        url: config.url,
        method: config.method,
        model: config.data?.model,
      });
      return config;
    },
    (error) => {
      logger.error('LLM请求拦截器错误', error);
      return Promise.reject(error);
    }
  );

  // 响应拦截器：记录响应日志
  client.interceptors.response.use(
    (response) => {
      logger.debug('LLM响应', {
        status: response.status,
        url: response.config.url,
      });
      return response;
    },
    (error) => {
      logger.error('LLM响应错误', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
      });
      return Promise.reject(error);
    }
  );

  return client;
};

/**
 * 调用LLM进行提示词润色
 * @param prompt 原始提示词
 * @returns 润色后的提示词
 */
export const enhancePromptWithLLM = async (prompt: string): Promise<string> => {
  logger.info('开始调用LLM进行提示词润色', { promptLength: prompt.length });

  const config = getLLMConfig();
  if (!config) {
    const errorMsg = 'LLM配置不完整，请检查环境变量：NEXT_PUBLIC_LLM_API_KEY, NEXT_PUBLIC_LLM_API_URL, NEXT_PUBLIC_LLM_MODEL';
    logger.error(errorMsg);
    throw new Error(errorMsg);
  }

  try {
    const client = createLLMClient(config);

    // 构建提示词
    const systemPrompt = '你是一个专业的提示词优化助手。请优化用户提供的图像生成提示词，使其更加详细、专业，并包含必要的质量描述词。保持原意不变，只进行优化和增强。直接返回优化后的提示词，不要添加任何解释或额外内容。';
    const userPrompt = `请优化以下提示词：\n\n${prompt}`;

    logger.debug('发送LLM请求', {
      model: config.model,
      promptLength: prompt.length,
    });

    // 调用LLM API（支持OpenAI兼容的API）
    const response = await client.post<OpenAIResponse | SimpleLLMResponse>(
      '/v1/chat/completions',
      {
        model: config.model,
        messages: [
          {
            role: 'system',
            content: systemPrompt,
          },
          {
            role: 'user',
            content: userPrompt,
          },
        ],
        temperature: 0.7,
        max_tokens: 1000,
      }
    );

    logger.debug('LLM响应数据', {
      status: response.status,
      hasData: !!response.data,
    });

    // 解析响应（支持OpenAI格式）
    let enhancedPrompt: string;
    const responseData = response.data;
    
    if (responseData && typeof responseData === 'object') {
      // OpenAI格式：response.data.choices[0].message.content
      if ('choices' in responseData && Array.isArray(responseData.choices) && responseData.choices.length > 0) {
        const choice = responseData.choices[0];
        if (choice && 'message' in choice && choice.message && 'content' in choice.message) {
          enhancedPrompt = String(choice.message.content).trim();
        } else {
          throw new Error('LLM响应格式错误：无法找到choices[0].message.content');
        }
      }
      // 其他格式：直接返回content
      else if ('content' in responseData) {
        enhancedPrompt = String((responseData as SimpleLLMResponse).content).trim();
      } else {
        logger.error('未知的LLM响应格式', responseData);
        throw new Error('LLM响应格式错误：无法解析响应内容');
      }
    } else {
      throw new Error('LLM响应格式错误：响应不是对象');
    }

    if (!enhancedPrompt || enhancedPrompt.length === 0) {
      throw new Error('LLM返回的润色结果为空');
    }

    logger.info('LLM润色完成', {
      originalLength: prompt.length,
      enhancedLength: enhancedPrompt.length,
    });

    return enhancedPrompt;
  } catch (error: any) {
    logger.error('LLM润色失败', {
      error: error.message,
      stack: error.stack,
      promptLength: prompt.length,
    });

    // 提供更友好的错误信息
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;
      
      if (status === 401) {
        throw new Error('LLM API密钥无效，请检查NEXT_PUBLIC_LLM_API_KEY配置');
      } else if (status === 404) {
        throw new Error('LLM API地址不存在，请检查NEXT_PUBLIC_LLM_API_URL配置');
      } else if (status === 429) {
        throw new Error('LLM API请求频率过高，请稍后重试');
      } else {
        throw new Error(`LLM API错误 (${status}): ${data?.error?.message || data?.message || '未知错误'}`);
      }
    } else if (error.request) {
      throw new Error('无法连接到LLM服务，请检查网络连接和NEXT_PUBLIC_LLM_API_URL配置');
    } else {
      throw new Error(`LLM润色失败: ${error.message}`);
    }
  }
};

