
export const getTechHeat = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/tech_heat');
    const result = await response.json();
    
    console.log('API返回的技术热度数据:', result);
    console.log('数据类型:', result.data);

    return result.data;
  } catch (error) {
    console.error('获取技术热度失败,使用模拟数据:', error);
    // 返回模拟数据
    const mockData = [
      { skill: 'Python', heat: 95, updated_at: new Date().toISOString() },
      { skill: 'JavaScript', heat: 88, updated_at: new Date().toISOString() },
      { skill: 'Java', heat: 85, updated_at: new Date().toISOString() },
      { skill: 'Go', heat: 75, updated_at: new Date().toISOString() },
      { skill: 'Rust', heat: 70, updated_at: new Date().toISOString() }
    ];
    return mockData;
  }
};