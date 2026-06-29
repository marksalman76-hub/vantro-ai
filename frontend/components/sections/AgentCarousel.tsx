'use client'

import { Swiper, SwiperSlide } from 'swiper/react'
import { Navigation, Pagination, Autoplay } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'

const AGENTS = [
  { id: 'head_agent', title: 'Head Agent / CEO', name: 'Victoria', category: 'Executive' },
  { id: 'strategist_agent', title: 'Strategist Agent', name: 'Marcus', category: 'Strategy' },
  { id: 'business_growth_partnerships_agent', title: 'Business Growth & Partnerships', name: 'Priya', category: 'Strategy' },
  { id: 'research_analytics_agent', title: 'Research & Analytics', name: 'David', category: 'Research' },
  { id: 'lead_generator_agent', title: 'Lead Generator', name: 'Sarah', category: 'Sales' },
  { id: 'sales_closer_agent', title: 'Sales Closer', name: 'James', category: 'Sales' },
  { id: 'crm_agent', title: 'CRM Agent', name: 'Elena', category: 'Sales' },
  { id: 'intake_trial_agent', title: 'Intake & Trial', name: 'Alex', category: 'Sales' },
  { id: 'marketing_specialist_agent', title: 'Marketing Specialist', name: 'Lisa', category: 'Marketing' },
  { id: 'social_media_content_agent', title: 'Social Media Content', name: 'Jordan', category: 'Marketing' },
  { id: 'seo_content_agent', title: 'SEO & Content', name: 'Sophie', category: 'Marketing' },
  { id: 'ads_optimisation_agent', title: 'Ads Optimisation', name: 'Mikhail', category: 'Marketing' },
  { id: 'influencer_outreach_agent', title: 'Influencer Outreach', name: 'Jasmine', category: 'Marketing' },
  { id: 'ugc_media_agent', title: 'UGC Media', name: 'Chris', category: 'Media' },
  { id: 'website_app_agent', title: 'Website / App', name: 'Emma', category: 'Digital' },
  { id: 'product_development_agent', title: 'Product Development', name: 'Gabriel', category: 'Digital' },
  { id: 'ecommerce_agent', title: 'Ecommerce', name: 'Olivia', category: 'Digital' },
  { id: 'customer_lifecycle_agent', title: 'Customer Lifecycle', name: 'Rachel', category: 'Support' },
  { id: 'email_reply_agent', title: 'Email Reply', name: 'Thomas', category: 'Support' },
  { id: 'review_reputation_agent', title: 'Review / Reputation', name: 'Nicole', category: 'Support' },
  { id: 'ops_automation_agent', title: 'Ops & Automation', name: 'Kevin', category: 'Operations' },
  { id: 'finance_admin_agent', title: 'Finance / Admin', name: 'Yuki', category: 'Operations' },
]

export default function AgentCarousel() {
  return (
    <section className="relative py-20 md:py-32 px-6 md:px-16 bg-gradient-to-b from-black via-slate-950 to-black">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="font-sans font-light text-4xl md:text-5xl text-white leading-tight mb-4">
            Meet Your Workforce
          </h2>
          <p className="text-lg text-white/55 max-w-2xl mx-auto">
            22 specialized agents, each trained for one domain. Plug in your workflow and let them run 24/7.
          </p>
        </div>

        {/* Carousel */}
        <div className="relative">
          <Swiper
            modules={[Navigation, Pagination, Autoplay]}
            slidesPerView={1}
            breakpoints={{
              640: { slidesPerView: 2, spaceBetween: 16 },
              1024: { slidesPerView: 3, spaceBetween: 20 },
              1280: { slidesPerView: 4, spaceBetween: 24 },
            }}
            navigation={{
              nextEl: '.agent-carousel-next',
              prevEl: '.agent-carousel-prev',
            }}
            pagination={{
              el: '.agent-carousel-pagination',
              clickable: true,
              dynamicBullets: true,
            }}
            autoplay={{ delay: 5000, disableOnInteraction: true }}
            loop
            className="agent-carousel"
          >
            {AGENTS.map((agent) => (
              <SwiperSlide key={agent.id} className="h-auto">
                <div className="group relative h-full rounded-xl border border-white/10 bg-gradient-to-br from-white/5 to-transparent p-6 transition-all duration-300 hover:border-white/20 hover:bg-gradient-to-br hover:from-white/10 hover:to-white/5">
                  {/* Category Badge */}
                  <div className="mb-6 inline-block px-3 py-1 rounded-full text-xs font-mono tracking-widest uppercase bg-white/5 text-white/40 border border-white/10">
                    {agent.category}
                  </div>

                  {/* Title (Position) */}
                  <h3 className="text-xl font-semibold text-white mb-2 line-clamp-2">
                    {agent.title}
                  </h3>

                  {/* Name */}
                  <p className="text-sm text-white/60 font-light">
                    {agent.name}
                  </p>

                  {/* Hover accent */}
                  <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-purple-500/10 to-transparent rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-0" />
                </div>
              </SwiperSlide>
            ))}
          </Swiper>

          {/* Navigation Buttons */}
          <button
            className="agent-carousel-prev absolute left-0 top-1/2 -translate-y-1/2 -translate-x-12 md:-translate-x-16 z-10 w-10 h-10 md:w-12 md:h-12 flex items-center justify-center rounded-full border border-white/20 text-white transition-all hover:bg-white hover:text-black"
            aria-label="Previous agent"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            className="agent-carousel-next absolute right-0 top-1/2 -translate-y-1/2 translate-x-12 md:translate-x-16 z-10 w-10 h-10 md:w-12 md:h-12 flex items-center justify-center rounded-full border border-white/20 text-white transition-all hover:bg-white hover:text-black"
            aria-label="Next agent"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>

          {/* Pagination */}
          <div className="agent-carousel-pagination mt-8 flex justify-center gap-2" />
        </div>
      </div>
    </section>
  )
}
