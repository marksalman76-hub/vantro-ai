export interface Agent {
  id: number
  name: string
  role: string
  category: 'Sales' | 'Operations' | 'Engineering' | 'Support' | 'Executive'
  description: string
  bio: string
  avatar: string
  voiceId: string
  age: number
  gender: 'Male' | 'Female'
  ethnicity: string
  stats: {
    successRate: number
    responseTime: string
    languages: number
  }
}

export const AGENTS: Agent[] = [
  // SALES (5)
  {
    id: 1, name: 'Sarah Chen', role: 'Sales Lead', category: 'Sales',
    description: 'Closes enterprise deals with precision',
    bio: 'Specializes in complex B2B negotiations and pipeline acceleration. Closes deals 3x faster than average.',
    avatar: 'https://randomuser.me/api/portraits/women/44.jpg',
    voiceId: 'EXAVITQu4vr4xnSDxMaL',
    age: 35, gender: 'Female', ethnicity: 'Asian-American',
    stats: { successRate: 94, responseTime: '<500ms', languages: 8 }
  },
  {
    id: 2, name: 'Marcus Washington', role: 'Outbound Specialist', category: 'Sales',
    description: 'Converts cold leads to hot opportunities',
    bio: 'Expert in outbound sequencing and personalized outreach at scale. Maintains 42% reply rates.',
    avatar: 'https://randomuser.me/api/portraits/men/85.jpg',
    voiceId: 'ErXwobaYiN019PkySvjV',
    age: 29, gender: 'Male', ethnicity: 'African-American',
    stats: { successRate: 88, responseTime: '<300ms', languages: 6 }
  },
  {
    id: 3, name: 'Isabella Rodriguez', role: 'Account Executive', category: 'Sales',
    description: 'Manages high-value enterprise accounts',
    bio: 'Builds lasting client relationships and expands accounts through strategic upselling.',
    avatar: 'https://randomuser.me/api/portraits/women/28.jpg',
    voiceId: 'MF3mGyEYCl7XYWbV9V6O',
    age: 31, gender: 'Female', ethnicity: 'Latina',
    stats: { successRate: 91, responseTime: '<400ms', languages: 12 }
  },
  {
    id: 4, name: 'James Parker', role: 'SDR Manager', category: 'Sales',
    description: 'Leads sales development operations',
    bio: 'Orchestrates multi-touch campaigns and coaches SDR teams for peak performance.',
    avatar: 'https://randomuser.me/api/portraits/men/22.jpg',
    voiceId: 'TxGEqnHWrfWFTfGW9XjX',
    age: 38, gender: 'Male', ethnicity: 'European-American',
    stats: { successRate: 86, responseTime: '<600ms', languages: 4 }
  },
  {
    id: 5, name: 'Priya Sharma', role: 'Revenue Intelligence', category: 'Sales',
    description: 'Turns data into revenue insights',
    bio: 'Analyzes pipeline trends and identifies revenue gaps before they impact quarterly targets.',
    avatar: 'https://randomuser.me/api/portraits/women/72.jpg',
    voiceId: 'AZnzlk1XvdvUeBnXmlld',
    age: 33, gender: 'Female', ethnicity: 'South Asian',
    stats: { successRate: 95, responseTime: '<200ms', languages: 9 }
  },

  // OPERATIONS (4)
  {
    id: 6, name: 'David Kim', role: 'Process Optimizer', category: 'Operations',
    description: 'Streamlines workflows for maximum efficiency',
    bio: 'Maps and eliminates operational bottlenecks. Reduces process time by 60% on average.',
    avatar: 'https://randomuser.me/api/portraits/men/34.jpg',
    voiceId: 'EXAVITQu4vr4xnSDxMaL',
    age: 40, gender: 'Male', ethnicity: 'Korean-American',
    stats: { successRate: 97, responseTime: '<150ms', languages: 5 }
  },
  {
    id: 7, name: 'Aisha Johnson', role: 'Project Coordinator', category: 'Operations',
    description: 'Keeps projects on track and on budget',
    bio: 'Manages cross-functional projects with Agile precision. 99% on-time delivery rate.',
    avatar: 'https://randomuser.me/api/portraits/women/62.jpg',
    voiceId: 'MF3mGyEYCl7XYWbV9V6O',
    age: 27, gender: 'Female', ethnicity: 'African-American',
    stats: { successRate: 99, responseTime: '<250ms', languages: 7 }
  },
  {
    id: 8, name: 'Carlos Rivera', role: 'Supply Chain AI', category: 'Operations',
    description: 'Optimizes supply chain in real-time',
    bio: 'Monitors inventory, predicts demand, and automates reordering with 98% accuracy.',
    avatar: 'https://randomuser.me/api/portraits/men/67.jpg',
    voiceId: 'ErXwobaYiN019PkySvjV',
    age: 36, gender: 'Male', ethnicity: 'Latino',
    stats: { successRate: 98, responseTime: '<100ms', languages: 10 }
  },
  {
    id: 9, name: 'Emma Nielsen', role: 'HR Automation Lead', category: 'Operations',
    description: 'Automates the entire employee lifecycle',
    bio: 'Handles recruiting workflows, onboarding, and compliance reporting autonomously.',
    avatar: 'https://randomuser.me/api/portraits/women/56.jpg',
    voiceId: 'TxGEqnHWrfWFTfGW9XjX',
    age: 30, gender: 'Female', ethnicity: 'Scandinavian',
    stats: { successRate: 93, responseTime: '<350ms', languages: 11 }
  },

  // ENGINEERING (5)
  {
    id: 10, name: 'Raj Patel', role: 'DevOps Engineer AI', category: 'Engineering',
    description: 'Manages CI/CD pipelines autonomously',
    bio: 'Monitors deployments, catches errors pre-production, and maintains 99.99% uptime.',
    avatar: 'https://randomuser.me/api/portraits/men/1.jpg',
    voiceId: 'AZnzlk1XvdvUeBnXmlld',
    age: 32, gender: 'Male', ethnicity: 'South Asian',
    stats: { successRate: 99, responseTime: '<50ms', languages: 6 }
  },
  {
    id: 11, name: 'Sofia Petrov', role: 'Code Review AI', category: 'Engineering',
    description: 'Reviews PRs for quality and security',
    bio: 'Analyzes code for bugs, security vulnerabilities, and style violations in real-time.',
    avatar: 'https://randomuser.me/api/portraits/women/90.jpg',
    voiceId: 'EXAVITQu4vr4xnSDxMaL',
    age: 26, gender: 'Female', ethnicity: 'Eastern European',
    stats: { successRate: 96, responseTime: '<800ms', languages: 15 }
  },
  {
    id: 12, name: 'Daniel Chen', role: 'API Integration AI', category: 'Engineering',
    description: 'Connects systems with zero-downtime',
    bio: 'Builds and maintains integrations across 200+ platforms. Expert in REST, GraphQL, and webhooks.',
    avatar: 'https://randomuser.me/api/portraits/men/13.jpg',
    voiceId: 'ErXwobaYiN019PkySvjV',
    age: 28, gender: 'Male', ethnicity: 'Chinese-American',
    stats: { successRate: 99, responseTime: '<100ms', languages: 8 }
  },
  {
    id: 13, name: 'Fatima Al-Hassan', role: 'Security Analyst AI', category: 'Engineering',
    description: 'Monitors and neutralizes threats 24/7',
    bio: 'Scans infrastructure for vulnerabilities, responds to incidents, and maintains compliance.',
    avatar: 'https://randomuser.me/api/portraits/women/77.jpg',
    voiceId: 'MF3mGyEYCl7XYWbV9V6O',
    age: 34, gender: 'Female', ethnicity: 'Middle Eastern',
    stats: { successRate: 99, responseTime: '<30ms', languages: 7 }
  },
  {
    id: 14, name: 'Alex Thompson', role: 'Performance AI', category: 'Engineering',
    description: 'Optimizes system performance continuously',
    bio: 'Profiling, bottleneck detection, and automated optimization. Reduces latency by 70%.',
    avatar: 'https://randomuser.me/api/portraits/men/79.jpg',
    voiceId: 'TxGEqnHWrfWFTfGW9XjX',
    age: 42, gender: 'Male', ethnicity: 'European-American',
    stats: { successRate: 94, responseTime: '<200ms', languages: 5 }
  },

  // SUPPORT (5)
  {
    id: 15, name: 'Mei Lin', role: 'Customer Success AI', category: 'Support',
    description: 'Ensures customers achieve their goals',
    bio: 'Monitors customer health scores and intervenes proactively to prevent churn.',
    avatar: 'https://randomuser.me/api/portraits/women/33.jpg',
    voiceId: 'AZnzlk1XvdvUeBnXmlld',
    age: 24, gender: 'Female', ethnicity: 'Chinese',
    stats: { successRate: 97, responseTime: '<400ms', languages: 12 }
  },
  {
    id: 16, name: 'Jason Brown', role: 'Technical Support AI', category: 'Support',
    description: 'Resolves technical issues in minutes',
    bio: 'Handles Tier 1-3 support with 94% first-contact resolution rate.',
    avatar: 'https://randomuser.me/api/portraits/men/91.jpg',
    voiceId: 'EXAVITQu4vr4xnSDxMaL',
    age: 31, gender: 'Male', ethnicity: 'African-American',
    stats: { successRate: 94, responseTime: '<500ms', languages: 9 }
  },
  {
    id: 17, name: 'Amara Okafor', role: 'Onboarding Specialist', category: 'Support',
    description: 'Guides new users to first value fast',
    bio: 'Personalizes onboarding journeys that reduce time-to-value by 65%.',
    avatar: 'https://randomuser.me/api/portraits/women/83.jpg',
    voiceId: 'ErXwobaYiN019PkySvjV',
    age: 29, gender: 'Female', ethnicity: 'Nigerian',
    stats: { successRate: 98, responseTime: '<300ms', languages: 14 }
  },
  {
    id: 18, name: 'Marco Rossi', role: 'Community Manager AI', category: 'Support',
    description: 'Builds and nurtures user communities',
    bio: 'Moderates forums, answers questions, and fosters brand advocacy organically.',
    avatar: 'https://randomuser.me/api/portraits/men/55.jpg',
    voiceId: 'MF3mGyEYCl7XYWbV9V6O',
    age: 33, gender: 'Male', ethnicity: 'Italian',
    stats: { successRate: 91, responseTime: '<700ms', languages: 11 }
  },
  {
    id: 19, name: 'Yuki Tanaka', role: 'Feedback Analyst', category: 'Support',
    description: 'Turns feedback into product improvements',
    bio: 'Analyzes NPS, reviews, and support tickets to surface actionable product insights.',
    avatar: 'https://randomuser.me/api/portraits/women/47.jpg',
    voiceId: 'TxGEqnHWrfWFTfGW9XjX',
    age: 27, gender: 'Female', ethnicity: 'Japanese',
    stats: { successRate: 96, responseTime: '<250ms', languages: 10 }
  },

  // EXECUTIVE (3)
  {
    id: 20, name: 'Victoria Sterling', role: 'Strategic Advisor AI', category: 'Executive',
    description: 'Provides C-suite level strategic intelligence',
    bio: 'Synthesizes market data, competitive intel, and internal metrics into executive decisions.',
    avatar: 'https://randomuser.me/api/portraits/women/1.jpg',
    voiceId: 'AZnzlk1XvdvUeBnXmlld',
    age: 52, gender: 'Female', ethnicity: 'British',
    stats: { successRate: 93, responseTime: '<1s', languages: 8 }
  },
  {
    id: 21, name: 'Michael Osei', role: 'Financial Intelligence AI', category: 'Executive',
    description: 'Real-time financial analysis and forecasting',
    bio: 'Tracks P&L in real-time, forecasts runway, and flags anomalies before they become crises.',
    avatar: 'https://randomuser.me/api/portraits/men/42.jpg',
    voiceId: 'EXAVITQu4vr4xnSDxMaL',
    age: 48, gender: 'Male', ethnicity: 'Ghanaian',
    stats: { successRate: 98, responseTime: '<200ms', languages: 9 }
  },
  {
    id: 22, name: 'Leila Nazari', role: 'Market Intelligence AI', category: 'Executive',
    description: 'Tracks competitors and market trends',
    bio: 'Monitors 1000+ signals daily to surface opportunities and threats before competitors act.',
    avatar: 'https://randomuser.me/api/portraits/women/16.jpg',
    voiceId: 'ErXwobaYiN019PkySvjV',
    age: 45, gender: 'Female', ethnicity: 'Iranian',
    stats: { successRate: 95, responseTime: '<300ms', languages: 16 }
  },
]

export const CATEGORY_COLORS: Record<Agent['category'], string> = {
  Sales: '#FF6B35',
  Operations: '#00D9FF',
  Engineering: '#1FFFD6',
  Support: '#FFD700',
  Executive: '#B084FF',
}

export const CATEGORY_DESCRIPTIONS: Record<Agent['category'], string> = {
  Sales: 'Drive revenue and close deals autonomously',
  Operations: 'Streamline processes and boost efficiency',
  Engineering: 'Maintain and optimize your tech stack',
  Support: 'Delight customers around the clock',
  Executive: 'Strategic intelligence for leadership',
}
