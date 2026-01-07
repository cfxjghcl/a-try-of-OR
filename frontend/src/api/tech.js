export const getTechHeat = async () => {
  console.log('🚀 尝试从后端获取数据...');
  
  try {
    // 先尝试直接调用后端
    const response = await fetch('http://localhost:5000/api/tech_heat');
    
    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ 成功获取后端数据:', data);
    return data;
    
  } catch (error) {
    console.warn('⚠️ 后端请求失败，使用模拟数据:', error);
    
    // 返回中文格式的模拟数据
    return [
      {"技术栈": "Python", "热度值": 95, "更新时间": new Date().toLocaleString()},
      {"技术栈": "JavaScript", "热度值": 88, "更新时间": new Date().toLocaleString()},
      {"技术栈": "Java", "热度值": 76, "更新时间": new Date().toLocaleString()},
      {"技术栈": "C++", "热度值": 65, "更新时间": new Date().toLocaleString()},
      {"技术栈": "Go", "热度值": 50, "更新时间": new Date().toLocaleString()},
      {"技术栈": "TypeScript", "热度值": 85, "更新时间": new Date().toLocaleString()},
      {"技术栈": "Vue.js", "热度值": 82, "更新时间": new Date().toLocaleString()},
      {"技术栈": "React", "热度值": 80, "更新时间": new Date().toLocaleString()},
      {"技术栈": "Spring Boot", "热度值": 75, "更新时间": new Date().toLocaleString()},
      {"技术栈": "Docker", "热度值": 70, "更新时间": new Date().toLocaleString()}
    ];
  }
};