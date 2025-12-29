export const getTechHeat = async () => {
  try {
    const response = await fetch('/api/tech_heat');
    const result = await response.json();
    
    // 根据你的后端API格式调整
    // 如果返回的是 { data: [...], ... } 格式
    if (result.data && Array.isArray(result.data)) {
      return result.data;
    } 
    // 如果直接返回数组
    else if (Array.isArray(result)) {
      return result;
    } 
    // 其他格式
    else {
      console.error('未知的数据格式:', result);
      return [];
    }
  } catch (error) {
    console.error('获取技术热度失败:', error);
    // 返回模拟数据用于测试
    return [
      { skill: 'facebook/react', heat: 2, updated_at: new Date().toISOString() },
      { skill: 'vercel/next.js', heat: 1, updated_at: new Date().toISOString() },
      { skill: 'microsoft/vscode', heat: 1, updated_at: new Date().toISOString() },
      { skill: 'pmndrs/zustand', heat: 1, updated_at: new Date().toISOString() },
      { skill: 'tailwindlabs/tailwindcss', heat: 1, updated_at: new Date().toISOString() },
      { skill: 'vitejs/vite', heat: 1, updated_at: new Date().toISOString() },
      { skill: 'nodejs/node', heat: 1, updated_at: new Date().toISOString() },
      { skill: 'mrdoob/three.js', heat: 1, updated_at: new Date().toISOString() },
      { skill: 'nestjs/nest', heat: 1, updated_at: new Date().toISOString() },
      { skill: 'vuejs/vue', heat: 1, updated_at: new Date().toISOString() }
    ];
  }
};