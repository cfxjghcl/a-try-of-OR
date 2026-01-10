<template>
  <div class="skill-detail-container">
    <!-- 1. 页面导航栏 -->
    <div class="skill-nav">
      <button @click="$router.back()" class="back-btn">← 返回</button>
      <h1 class="skill-title">{{ skillInfo.name }} 技能详情</h1>
    </div>

    <!-- 加载中提示 -->
    <div v-if="loading" class="loading">正在加载技能数据...</div>

    <div v-else class="skill-content">
      <!-- 2. 技能基础信息卡片 -->
      <div class="skill-base-card">
        <div class="base-item">
          <span class="label">所属领域：</span>
          <span class="value">{{ skillInfo.field || "暂无数据" }}</span>
        </div>
        <div class="base-item">
          <span class="label">关联专业：</span>
          <span class="value">{{ skillInfo.relatedMajor?.join("、") || "暂无数据" }}</span>
        </div>
        <div class="base-item">
          <span class="label">关联职业：</span>
          <span class="value">{{ skillInfo.relatedCareer?.join("、") || "暂无数据" }}</span>
        </div>
        <div class="base-item">
          <span class="label">掌握难度：</span>
          <div class="difficulty-bar">
            <div class="difficulty-fill" :style="{ width: skillInfo.difficulty + '%' }"></div>
          </div>
          <span class="difficulty-text">{{ skillInfo.difficulty }}%</span>
        </div>
      </div>

      <!-- 3. 入门推荐与建议 -->
      <div class="skill-intro-card">
        <h2 class="card-title">入门推荐与建议</h2>
        <div class="intro-content">
          <div class="intro-item">
            <h3 class="item-title">✅ 入门前提</h3>
            <ul class="intro-list">
              <li v-for="(item, index) in skillIntro.prerequisite" :key="index">{{ item }}</li>
            </ul>
          </div>
          <div class="intro-item">
            <h3 class="item-title">📚 入门学习路径</h3>
            <div class="path-list">
              <div 
                v-for="(stage, index) in skillIntro.learningPath" 
                :key="index" 
                class="path-stage"
              >
                <span class="stage-num">第{{ index + 1 }}阶段</span>
                <div class="stage-content">{{ stage.content }}</div>
                <span class="stage-target">目标：{{ stage.target }}</span>
              </div>
            </div>
          </div>
          <div class="intro-item">
            <h3 class="item-title">💡 入门避坑建议</h3>
            <ul class="intro-list">
              <li v-for="(item, index) in skillIntro.tips" :key="index">{{ item }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 4. 学习渠道推荐 -->
      <div class="skill-channel-card">
        <h2 class="card-title">学习渠道推荐</h2>
        <div class="channel-tabs">
          <button 
            v-for="tab in channelTabs" 
            :key="tab.type"
            class="tab-btn"
            :class="{ active: activeTab === tab.type }"
            @click="activeTab = tab.type"
          >
            {{ tab.name }}
          </button>
        </div>
        <div class="channel-list">
          <a 
            v-for="(channel, index) in filterChannels" 
            :key="index" 
            :href="channel.url" 
            target="_blank" 
            class="channel-item"
          >
            <div class="channel-icon">{{ getChannelIcon(channel.type) }}</div>
            <div class="channel-info">
              <h4 class="channel-name">{{ channel.name }}</h4>
              <p class="channel-desc">{{ channel.desc }}</p>
              <span class="channel-tag">{{ channel.level }}</span>
            </div>
          </a>
        </div>
      </div>

      <!-- 5. 长期目标规划 -->
      <div class="skill-plan-card">
        <h2 class="card-title">长期目标规划（1-3年）</h2>
        <div class="plan-timeline">
          <div 
            v-for="(plan, index) in longTermPlan" 
            :key="index" 
            class="plan-item"
          >
            <div class="plan-time">{{ plan.period }}</div>
            <div class="plan-content">
              <h3 class="plan-title">{{ plan.title }}</h3>
              <ul class="plan-list">
                <li v-for="(item, i) in plan.goals" :key="i">{{ item }}</li>
              </ul>
              <div class="plan-suggest">💡 规划建议：{{ plan.suggest }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 6. 技能进阶资源 -->
      <div class="skill-advanced-card">
        <h2 class="card-title">技能进阶资源</h2>
        <div class="advanced-list">
          <div 
            v-for="(resource, index) in advancedResources" 
            :key="index" 
            class="advanced-item"
          >
            <span class="resource-type">{{ resource.type }}</span>
            <a :href="resource.url" target="_blank" class="resource-name">{{ resource.name }}</a>
            <p class="resource-desc">{{ resource.desc }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// 初始化路由和参数
const router = useRouter()
const route = useRoute()
const skillId = route.params.id // 获取技能ID
const loading = ref(true) // 加载状态

// 1. 技能基础信息
const skillInfo = ref({
  name: '', // 技能名称
  field: '', // 所属领域
  relatedMajor: [], // 关联专业
  relatedCareer: [], // 关联职业
  difficulty: 0 // 掌握难度（0-100）
})

// 2. 入门推荐与建议
const skillIntro = ref({
  prerequisite: [], // 入门前提
  learningPath: [], // 入门学习路径
  tips: [] // 避坑建议
})

// 3. 学习渠道数据
const channelTabs = ref([
  { type: 'video', name: '视频教程' },
  { type: 'document', name: '文档书籍' },
  { type: 'practice', name: '实战平台' },
  { type: 'community', name: '社区交流' }
])
const activeTab = ref('video') // 默认选中视频教程
const skillChannels = ref([]) // 所有学习渠道

// 4. 长期目标规划
const longTermPlan = ref([])

// 5. 进阶资源
const advancedResources = ref([])

// 过滤当前标签的学习渠道
const filterChannels = computed(() => {
  return skillChannels.value.filter(channel => channel.type === activeTab.value)
})

// 获取渠道图标
const getChannelIcon = (type) => {
  const iconMap = {
    video: '🎬',
    document: '📖',
    practice: '💻',
    community: '👥'
  }
  return iconMap[type] || '📚'
}

// 6. 模拟调用OpenDigger API获取技能数据
const getSkillData = async () => {
  try {
    loading.value = true
    // 模拟接口请求延迟
    await new Promise(resolve => setTimeout(resolve, 800))

    // 模拟OpenDigger返回的技能数据（真实项目替换为API请求）
    const openDiggerMockData = {
      skillInfo: {
        name: 'Python编程',
        field: '编程语言/后端开发',
        relatedMajor: ['计算机科学与技术', '软件工程', '数据科学与大数据技术'],
        relatedCareer: ['Python后端开发工程师', '大数据工程师', '人工智能算法工程师'],
        difficulty: 65 // 掌握难度65%
      },
      skillIntro: {
        prerequisite: [
          '掌握基本的计算机操作（Windows/Mac/Linux）',
          '了解简单的编程逻辑（变量、循环、条件判断）',
          '无需提前掌握其他编程语言，零基础可入门'
        ],
        learningPath: [
          {
            content: '学习Python基础语法（变量、数据类型、运算符、流程控制）',
            target: '能独立编写简单的控制台程序（如计算器、猜数字游戏）'
          },
          {
            content: '学习Python函数、面向对象、模块与包',
            target: '能封装代码，实现模块化开发'
          },
          {
            content: '学习常用库（NumPy/Pandas/Requests）',
            target: '能处理数据、调用API接口'
          },
          {
            content: '实战小项目（爬虫、数据分析、简易Web应用）',
            target: '能独立完成小型实战项目'
          }
        ],
        tips: [
          '不要死记硬背语法，多敲代码多练习',
          '优先掌握核心知识点，不要过早陷入细节（如GIL、装饰器底层）',
          '遇到问题先查官方文档，再查社区（Stack Overflow/CSDN）',
          '定期复盘代码，优化写法，培养良好的编码习惯'
        ]
      },
      skillChannels: [
        // 视频教程
        {
          type: 'video',
          name: '尚硅谷Python零基础教程',
          desc: '零基础入门，从语法到实战全覆盖，适合纯新手',
          url: 'https://www.bilibili.com/video/BV1wD4y1o7AS/',
          level: '入门'
        },
        {
          type: 'video',
          name: '黑马程序员Python进阶教程',
          desc: '从基础到进阶，包含面向对象、并发编程、项目实战',
          url: 'https://www.bilibili.com/video/BV1qW4y1a7fU/',
          level: '进阶'
        },
        // 文档书籍
        {
          type: 'document',
          name: 'Python官方文档',
          desc: '最权威的Python学习资料，涵盖所有版本的语法和标准库',
          url: 'https://docs.python.org/zh-cn/3/',
          level: '全阶段'
        },
        {
          type: 'document',
          name: '《Python编程：从入门到实践》',
          desc: '零基础友好，理论+实战结合，适合入门学习',
          url: 'https://book.douban.com/subject/26829017/',
          level: '入门'
        },
        // 实战平台
        {
          type: 'practice',
          name: 'LeetCode Python题库',
          desc: '刷算法题巩固Python语法，提升编程思维',
          url: 'https://leetcode.cn/problemset/all/?listId=2cktkvj&topicSlugs=python',
          level: '进阶'
        },
        {
          type: 'practice',
          name: '牛客网Python实战题',
          desc: '包含基础语法、爬虫、数据分析等实战题型',
          url: 'https://www.nowcoder.com/ta/python-code',
          level: '入门-进阶'
        },
        // 社区交流
        {
          type: 'community',
          name: 'Python中文社区',
          desc: '国内最大的Python社区，可提问、交流、找学习资源',
          url: 'https://www.python.org.cn/',
          level: '全阶段'
        },
        {
          type: 'community',
          name: 'Stack Overflow Python板块',
          desc: '全球最大的程序员问答社区，解决Python各类问题',
          url: 'https://stackoverflow.com/questions/tagged/python',
          level: '全阶段'
        }
      ],
      longTermPlan: [
        {
          period: '第1年（入门-熟练）',
          title: '夯实基础，掌握核心技能',
          goals: [
            '熟练掌握Python核心语法和常用标准库',
            '完成3-5个小型实战项目（如爬虫、数据分析、简易Web应用）',
            '掌握至少1个主流框架（Django/FastAPI）',
            '了解数据库基础（MySQL/Redis）'
          ],
          suggest: '每周保证15+小时的学习时间，多敲代码少看视频，遇到问题独立解决'
        },
        {
          period: '第2年（熟练-精通）',
          title: '技术深化，积累项目经验',
          goals: [
            '深入学习Python高级特性（装饰器、生成器、并发编程）',
            '参与中型项目开发（开源项目/企业实习项目）',
            '掌握性能优化、代码调试、单元测试技能',
            '了解云原生技术（Docker/云服务器部署）'
          ],
          suggest: '关注行业前沿技术，参与技术社区分享，建立个人技术博客'
        },
        {
          period: '第3年（精通-专精）',
          title: '方向专精，形成技术壁垒',
          goals: [
            '选定细分方向深耕（如数据分析/AI/后端架构）',
            '主导大型项目的核心模块开发',
            '掌握架构设计、技术选型能力',
            '具备独立解决复杂技术问题的能力'
          ],
          suggest: '持续学习+输出，通过开源贡献、技术分享提升个人影响力'
        }
      ],
      advancedResources: [
        {
          type: '进阶书籍',
          name: '《Fluent Python》',
          desc: 'Python进阶必读，深入理解Python高级特性和最佳实践',
          url: 'https://book.douban.com/subject/27028517/'
        },
        {
          type: '开源项目',
          name: 'Django官方开源项目',
          desc: '学习工业级Python Web框架的设计思想和源码实现',
          url: 'https://github.com/django/django'
        },
        {
          type: '技术专栏',
          name: 'Python开发者官方专栏',
          desc: '涵盖Python最新特性、性能优化、实战技巧',
          url: 'https://realpython.com/'
        },
        {
          type: '实战课程',
          name: '极客时间《Python核心技术与实战》',
          desc: '从基础到进阶，覆盖Python全栈开发核心技能',
          url: 'https://time.geekbang.org/column/intro/100027601'
        }
      ]
    }

    // 赋值到页面数据
    skillInfo.value = openDiggerMockData.skillInfo
    skillIntro.value = openDiggerMockData.skillIntro
    skillChannels.value = openDiggerMockData.skillChannels
    longTermPlan.value = openDiggerMockData.longTermPlan
    advancedResources.value = openDiggerMockData.advancedResources
  } catch (error) {
    console.error('获取技能数据失败：', error)
    alert('数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 生命周期钩子：页面挂载时加载数据
onMounted(() => {
  getSkillData()
})
</script>

<style scoped>
/* 全局容器 */
.skill-detail-container {
  width: 90%;
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  font-family: "Microsoft Yahei", sans-serif;
  color: #333;
  box-sizing: border-box;
}

/* 导航栏 */
.skill-nav {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}
.back-btn {
  padding: 8px 15px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 20px;
  transition: background-color 0.3s;
}
.back-btn:hover {
  background-color: #0056b3;
}
.skill-title {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

/* 加载中 */
.loading {
  text-align: center;
  padding: 50px 0;
  font-size: 16px;
  color: #666;
}

/* 内容容器 */
.skill-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 基础信息卡片 */
.skill-base-card {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.base-item {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
  font-size: 16px;
  line-height: 1.6;
}
.base-item:last-child {
  margin-bottom: 0;
}
.label {
  font-weight: bold;
  width: 120px;
  color: #555;
  flex-shrink: 0;
}
.value {
  flex: 1;
  color: #333;
}
.difficulty-bar {
  width: 200px;
  height: 10px;
  background-color: #eee;
  border-radius: 5px;
  margin: 0 10px;
  flex-shrink: 0;
}
.difficulty-fill {
  height: 100%;
  background-color: #dc3545;
  border-radius: 5px;
  transition: width 0.5s ease;
}
.difficulty-text {
  color: #dc3545;
  font-weight: bold;
  width: 50px;
  text-align: right;
  flex-shrink: 0;
}

/* 通用卡片标题 */
.card-title {
  font-size: 20px;
  font-weight: bold;
  margin: 0 0 20px 0;
  color: #2c3e50;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

/* 入门推荐卡片 */
.skill-intro-card {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.intro-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}
.intro-item {
  margin-bottom: 15px;
}
.intro-item:last-child {
  margin-bottom: 0;
}
.item-title {
  font-size: 18px;
  margin: 0 0 12px 0;
  color: #007bff;
}
.intro-list {
  padding-left: 20px;
  font-size: 16px;
  line-height: 1.8;
  margin: 0;
  color: #333;
}
.intro-list li {
  margin-bottom: 8px;
}
.intro-list li:last-child {
  margin-bottom: 0;
}
.path-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.path-stage {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}
.stage-num {
  font-weight: bold;
  color: #007bff;
  font-size: 16px;
}
.stage-content {
  font-size: 16px;
  line-height: 1.6;
  color: #333;
}
.stage-target {
  font-size: 14px;
  color: #666;
  font-style: italic;
}

/* 学习渠道卡片 */
.skill-channel-card {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.channel-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.tab-btn {
  padding: 8px 15px;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 16px;
}
.tab-btn.active {
  background-color: #007bff;
  color: #fff;
  border-color: #007bff;
}
.channel-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}
.channel-item {
  display: flex;
  gap: 15px;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  transition: all 0.3s;
}
.channel-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #007bff;
  transform: translateY(-2px);
}
.channel-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  border-radius: 50%;
  flex-shrink: 0;
}
.channel-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.channel-name {
  font-size: 16px;
  font-weight: bold;
  margin: 0;
  color: #2c3e50;
}
.channel-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.5;
}
.channel-tag {
  font-size: 12px;
  padding: 3px 8px;
  background-color: #e9ecef;
  border-radius: 12px;
  width: fit-content;
}

/* 长期规划卡片 */
.skill-plan-card {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.plan-timeline {
  position: relative;
  padding-left: 30px;
}
.plan-timeline::before {
  content: '';
  position: absolute;
  left: 10px;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: #007bff;
}
.plan-item {
  position: relative;
  margin-bottom: 30px;
}
.plan-item:last-child {
  margin-bottom: 0;
}
.plan-item::before {
  content: '';
  position: absolute;
  left: -30px;
  top: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: #007bff;
}
.plan-time {
  font-weight: bold;
  color: #007bff;
  font-size: 16px;
  margin-bottom: 8px;
}
.plan-content {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}
.plan-title {
  font-size: 18px;
  margin: 0 0 10px 0;
  color: #2c3e50;
}
.plan-list {
  padding-left: 20px;
  font-size: 16px;
  line-height: 1.8;
  margin: 0 0 10px 0;
  color: #333;
}
.plan-suggest {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  font-style: italic;
}

/* 进阶资源卡片 */
.skill-advanced-card {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}
.advanced-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.advanced-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}
.resource-type {
  font-size: 12px;
  padding: 3px 8px;
  background-color: #007bff;
  color: #fff;
  border-radius: 12px;
  width: fit-content;
}
.resource-name {
  font-size: 16px;
  font-weight: bold;
  color: #007bff;
  text-decoration: none;
}
.resource-name:hover {
  text-decoration: underline;
}
.resource-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.6;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .skill-detail-container {
    width: 95%;
    padding: 15px;
  }
  .skill-title {
    font-size: 20px;
  }
  .card-title {
    font-size: 18px;
  }
  .item-title {
    font-size: 16px;
  }
  .base-item {
    flex-direction: column;
    align-items: flex-start;
  }
  .label {
    margin-bottom: 5px;
  }
  .difficulty-bar {
    width: 100%;
    margin: 5px 0;
  }
  .difficulty-text {
    align-self: flex-start;
    margin-top: 5px;
  }
  .channel-list {
    grid-template-columns: 1fr;
  }
  .plan-timeline {
    padding-left: 20px;
  }
  .plan-item::before {
    left: -20px;
  }
}
</style>