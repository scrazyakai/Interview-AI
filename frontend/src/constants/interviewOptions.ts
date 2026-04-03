export const jobTitleOptions = ['前端', '后端', '测试', '运维', '全栈'] as const

export const experienceLevelOptions = [
  { label: '应届生', value: 'intern' },
  { label: '初级', value: 'junior' },
  { label: '中级', value: 'mid' },
  { label: '高级', value: 'senior' },
] as const

export const modeOptions = [
  { value: 'technical', label: '技术面' },
  { value: 'behavioral', label: '行为面' },
  { value: 'mixed', label: '综合面' },
] as const

export type ExperienceLevelValue = (typeof experienceLevelOptions)[number]['value']
