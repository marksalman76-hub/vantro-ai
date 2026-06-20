"use client";

import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  Award,
  Check,
  ChevronDown,
  Menu,
  Search,
  ShieldCheck,
  ShoppingBag,
  Sparkles,
  Star,
  Timer,
  User,
  X,
} from "lucide-react";
import styles from "./page.module.css";

const heroSlides = [
  { label: "Studio product", caption: "Medical-grade silicone with dual-zone bristles", tone: "ivory" },
  { label: "Morning ritual", caption: "Designed to glide upward with serum or facial oil", tone: "rose" },
  { label: "Contour detail", caption: "Curved handle for jawline, cheekbone, and neck massage", tone: "gold" },
  { label: "Travel ready", caption: "A 3-minute ritual that fits on every vanity", tone: "linen" },
];

const benefits = [
  { icon: ShieldCheck, title: "Lymphatic Drainage", text: "Reduces puffiness in 7 days with clinically designed bristles." },
  { icon: Sparkles, title: "Sculpts & Lifts", text: "Defines the jawline and tightens cheeks naturally." },
  { icon: Award, title: "Boosts Glow", text: "Improves circulation and helps serums absorb evenly." },
  { icon: Timer, title: "Quick Ritual", text: "Visible-care routine in 3 to 5 minutes daily." },
];

const results = [
  { name: "Sarah L.", location: "New York", quote: "Puffiness was gone in week one. My face looks slimmer instantly.", before: "Week 0", after: "Week 4" },
  { name: "Jessica M.", location: "Los Angeles", quote: "Three minutes and I look like I got a facial before work.", before: "Before", after: "After" },
  { name: "Mina R.", location: "Chicago", quote: "My cheekbones look lifted and my skin has that soft glass glow.", before: "AM puffiness", after: "Daily ritual" },
  { name: "Amanda K.", location: "Miami", quote: "My jaw is more defined. Best thing I have bought all year.", before: "Day 1", after: "Day 28" },
  { name: "Priya S.", location: "Austin", quote: "Gentle enough for my sensitive skin, but I still see a difference.", before: "Before", after: "4 weeks" },
  { name: "Olivia B.", location: "Seattle", quote: "It makes my skincare feel intentional, quick, and genuinely luxe.", before: "Tired skin", after: "Lifted glow" },
];

const steps = [
  { kicker: "Step 1", title: "Morning Ritual", text: "Apply your favorite serum or oil. Glide the brush upward from neck to jaw, then cheekbone to temple." },
  { kicker: "Step 2", title: "Lymphatic Flow", text: "The bristle pattern stimulates facial lymph pathways to help release fluid retention naturally." },
  { kicker: "Step 3", title: "Visible Results", text: "Notice a fresher look within days, with sculpting effects building through consistent daily use." },
];

const specs = [
  "Medical-grade silicone bristles",
  "Ergonomic contoured handle",
  "2 bristle zones: fine and massage",
  "Lasts 2+ years with proper care",
  "Dermatologist approved",
  "Easy to clean in warm water",
];

const ugcReviews = [
  { name: "Sarah L.", location: "New York", quote: "Puffiness gone in week one. My face looks slimmer instantly." },
  { name: "Jessica M.", location: "Los Angeles", quote: "This actually works. Three minutes and I look like I got a facial." },
  { name: "Amanda K.", location: "Miami", quote: "My jaw is more defined. Best thing I have bought all year." },
  { name: "Nora P.", location: "Denver", quote: "I use it every morning. My serum absorbs better and I look awake." },
  { name: "Camille D.", location: "Boston", quote: "The ritual feels expensive, but it takes almost no time." },
];

const writtenReviews = [
  { name: "Leah W.", location: "San Diego", quote: "I noticed my face looked more sculpted after just two uses. The biggest change is morning puffiness around my cheeks." },
  { name: "Maya H.", location: "Brooklyn", quote: "It is gentle, easy to clean, and beautiful enough to leave on my counter. I finally stick to a facial massage routine." },
  { name: "Grace T.", location: "Portland", quote: "I bought it for the glow, but the jawline definition surprised me. It makes skincare feel like a spa appointment." },
];

const faqs = [
  { q: "How long does it take to see results?", a: "Most customers notice reduced puffiness within 3 to 7 days. Full sculpting effects build after about 4 weeks of consistent use." },
  { q: "Is it safe for all skin types?", a: "Yes. The medical-grade silicone is gentle, hygienic, and dermatologist approved for sensitive skin." },
  { q: "How often should I use it?", a: "Use it for 3 to 5 minutes daily, either in the morning to depuff or at night to relax facial tension." },
  { q: "Will it irritate my skin?", a: "No. The hypoallergenic silicone is designed to glide smoothly, especially when paired with serum or facial oil." },
  { q: "What is your return policy?", a: "You are covered by a 30-day money-back guarantee. If you do not love your results, you can request a full refund." },
  { q: "Can I use it with other products?", a: "Yes. It pairs beautifully with hydrating serums, facial oils, and moisturizers, and can improve product spread." },
];

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0 },
};

function Stars() {
  return (
    <span className={styles.stars} aria-label="5 star rating">
      {Array.from({ length: 5 }).map((_, index) => (
        <Star key={index} size={15} fill="currentColor" />
      ))}
    </span>
  );
}

function AddToCartButton({ compact = false }: { compact?: boolean }) {
  return (
    <button
      className={`${styles.primaryButton} ${compact ? styles.primaryButtonCompact : ""}`}
      onClick={() => window.dispatchEvent(new CustomEvent("aliaa:add_to_cart", { detail: { value: 26.99 } }))}
      type="button"
    >
      <ShoppingBag size={18} />
      Add to Cart - $26.99
    </button>
  );
}

function ProductVisual({ tone, label }: { tone: string; label: string }) {
  return (
    <div className={`${styles.productVisual} ${styles[`tone_${tone}`]}`}>
      <div className={styles.photoHalo} />
      <div className={styles.brushRender} aria-label={label} role="img">
        <span className={styles.brushHandle} />
        <span className={styles.brushHead}>
          {Array.from({ length: 24 }).map((_, index) => (
            <i key={index} />
          ))}
        </span>
      </div>
      <div className={styles.visualCaption}>{label}</div>
    </div>
  );
}

function ResultPortrait({ type, label, index }: { type: "before" | "after"; label: string; index: number }) {
  return (
    <div className={`${styles.resultPortrait} ${type === "after" ? styles.resultAfter : ""}`}>
      <span>{label}</span>
      <div className={styles.faceMockup}>
        <i style={{ transform: `translateX(${type === "after" ? 8 : -4}px) rotate(${index % 2 ? -5 : 4}deg)` }} />
      </div>
    </div>
  );
}

export default function AliaaProductPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [heroIndex, setHeroIndex] = useState(0);
  const [resultIndex, setResultIndex] = useState(0);
  const [ugcIndex, setUgcIndex] = useState(0);
  const [openFaq, setOpenFaq] = useState(0);

  useEffect(() => {
    const heroTimer = window.setInterval(() => setHeroIndex((current) => (current + 1) % heroSlides.length), 5000);
    const resultTimer = window.setInterval(() => setResultIndex((current) => (current + 1) % results.length), 5000);
    const ugcTimer = window.setInterval(() => setUgcIndex((current) => (current + 1) % ugcReviews.length), 4200);
    return () => {
      window.clearInterval(heroTimer);
      window.clearInterval(resultTimer);
      window.clearInterval(ugcTimer);
    };
  }, []);

  const activeResult = results[resultIndex];
  const visibleUgc = useMemo(() => [0, 1, 2].map((offset) => ugcReviews[(ugcIndex + offset) % ugcReviews.length]), [ugcIndex]);

  return (
    <main className={styles.page}>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Product",
            name: "aliaa Lymphatic Brush",
            brand: { "@type": "Brand", name: "aliaa" },
            description: "Premium facial lymphatic drainage and sculpting brush.",
            offers: { "@type": "Offer", price: "26.99", priceCurrency: "USD", availability: "https://schema.org/InStock" },
            aggregateRating: { "@type": "AggregateRating", ratingValue: "4.9", reviewCount: "3200" },
          }),
        }}
      />

      <header className={styles.nav}>
        <button className={styles.iconButton} type="button" aria-label="Open menu" onClick={() => setMobileMenuOpen(true)}>
          <Menu size={20} />
        </button>
        <a className={styles.logo} href="#top" aria-label="aliaa home">aliaa<span>tm</span></a>
        <nav className={styles.navLinks} aria-label="Primary navigation">
          <a href="#results">Results</a>
          <a href="#how">How it works</a>
          <a href="#reviews">Reviews</a>
          <a href="#faq">FAQ</a>
        </nav>
        <div className={styles.navActions}>
          <button className={styles.iconButton} type="button" aria-label="Search"><Search size={20} /></button>
          <button className={styles.iconButton} type="button" aria-label="Account"><User size={20} /></button>
          <button className={styles.cartButton} type="button" aria-label="Cart with one item"><ShoppingBag size={19} /><span>1</span></button>
        </div>
      </header>

      <AnimatePresence>
        {mobileMenuOpen ? (
          <motion.div className={styles.mobileMenu} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <button className={styles.mobileClose} type="button" aria-label="Close menu" onClick={() => setMobileMenuOpen(false)}>
              <X size={22} />
            </button>
            {[
              ["Results", "results"],
              ["How it works", "how"],
              ["Reviews", "reviews"],
              ["FAQ", "faq"],
            ].map(([label, href]) => (
              <a key={label} href={`#${href}`} onClick={() => setMobileMenuOpen(false)}>{label}</a>
            ))}
          </motion.div>
        ) : null}
      </AnimatePresence>

      <section className={styles.hero} id="top">
        <div className={styles.heroGrid}>
          <motion.div className={styles.gallery} initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.7 }}>
            <AnimatePresence mode="wait">
              <motion.div key={heroSlides[heroIndex].label} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.45 }}>
                <ProductVisual tone={heroSlides[heroIndex].tone} label={heroSlides[heroIndex].label} />
              </motion.div>
            </AnimatePresence>
            <div className={styles.galleryControls}>
              {heroSlides.map((slide, index) => (
                <button key={slide.label} className={index === heroIndex ? styles.activeDot : styles.dot} onClick={() => setHeroIndex(index)} type="button" aria-label={`Show ${slide.label}`} />
              ))}
            </div>
            <p>{heroSlides[heroIndex].caption}</p>
          </motion.div>

          <motion.div className={styles.heroCopy} initial="hidden" animate="visible" variants={fadeUp} transition={{ duration: 0.7, delay: 0.15 }}>
            <div className={styles.ratingLine}><Stars /> 4.9/5 stars | 3,200+ verified reviews</div>
            <h1>Sculpt Your Best Face in 3 Minutes</h1>
            <p className={styles.subheadline}>Lymphatic drainage + facial contouring in one ergonomic brush.</p>
            <div className={styles.priceRow}><strong>$26.99</strong><span>Premium facial tool</span></div>
            <div className={styles.heroActions}>
              <AddToCartButton />
              <a className={styles.secondaryButton} href="#results">See Before & Afters</a>
            </div>
            <div className={styles.trustGrid}>
              <span><Check size={16} /> 30-day money-back guarantee</span>
              <span><Check size={16} /> Ships within 24 hours</span>
              <span><Check size={16} /> 27,000+ glowing customers</span>
            </div>
          </motion.div>
        </div>
      </section>

      <section className={styles.benefits} aria-label="Quick benefits">
        {benefits.map((benefit, index) => {
          const Icon = benefit.icon;
          return (
            <motion.article key={benefit.title} className={styles.benefitCard} initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.4 }} variants={fadeUp} transition={{ duration: 0.5, delay: index * 0.06 }}>
              <Icon size={24} />
              <h2>{benefit.title}</h2>
              <p>{benefit.text}</p>
            </motion.article>
          );
        })}
      </section>

      <section className={styles.section} id="results">
        <div className={styles.sectionHeader}>
          <span>Real customers</span>
          <h2>Real Skin. Real Results. No Filters.</h2>
          <p>See how customers transformed puffiness, facial tension, and glow in just 4 weeks.</p>
        </div>
        <div className={styles.resultsShell}>
          <button className={styles.carouselArrow} type="button" aria-label="Previous result" onClick={() => setResultIndex((current) => (current - 1 + results.length) % results.length)}><ArrowLeft size={20} /></button>
          <AnimatePresence mode="wait">
            <motion.div key={activeResult.name} className={styles.resultCard} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }} transition={{ duration: 0.38 }}>
              <div className={styles.resultImages}>
                <ResultPortrait type="before" label={activeResult.before} index={resultIndex} />
                <ResultPortrait type="after" label={activeResult.after} index={resultIndex} />
              </div>
              <div className={styles.resultQuote}>
                <Stars />
                <blockquote>"{activeResult.quote}"</blockquote>
                <p>{activeResult.name} | {activeResult.location}</p>
              </div>
            </motion.div>
          </AnimatePresence>
          <button className={styles.carouselArrow} type="button" aria-label="Next result" onClick={() => setResultIndex((current) => (current + 1) % results.length)}><ArrowRight size={20} /></button>
        </div>
        <div className={styles.dots}>
          {results.map((result, index) => (
            <button key={result.name} className={index === resultIndex ? styles.activeDot : styles.dot} type="button" aria-label={`Show result from ${result.name}`} onClick={() => setResultIndex(index)} />
          ))}
        </div>
        <a className={styles.centerLink} href="#reviews">See all results</a>
      </section>

      <section className={styles.section} id="how">
        <div className={styles.sectionHeader}>
          <span>3-minute ritual</span>
          <h2>How It Works</h2>
          <p>Subtle pressure, upward movement, and consistent flow are the whole secret.</p>
        </div>
        <div className={styles.timeline}>
          {steps.map((step, index) => (
            <motion.article key={step.title} className={styles.stepCard} initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.35 }} variants={fadeUp} transition={{ duration: 0.5, delay: index * 0.08 }}>
              <div className={styles.stepVisual}>{index + 1}</div>
              <span>{step.kicker}</span>
              <h3>{step.title}</h3>
              <p>{step.text}</p>
            </motion.article>
          ))}
        </div>
      </section>

      <section className={`${styles.section} ${styles.specSection}`}>
        <ProductVisual tone="gold" label="Detail view" />
        <div>
          <span className={styles.eyebrow}>Features & specifications</span>
          <h2>Designed for delicate skin and daily sculpting.</h2>
          <ul className={styles.specList}>
            {specs.map((spec) => <li key={spec}><Check size={18} /> {spec}</li>)}
          </ul>
        </div>
      </section>

      <section className={styles.section} id="reviews">
        <div className={styles.sectionHeader}>
          <span>Verified purchases</span>
          <h2>Daily rituals, visible glow.</h2>
          <p>UGC-style review cards built for fast scanning and strong social proof.</p>
        </div>
        <div className={styles.ugcHeader}>
          <button className={styles.carouselArrow} type="button" aria-label="Previous testimonial" onClick={() => setUgcIndex((current) => (current - 1 + ugcReviews.length) % ugcReviews.length)}><ArrowLeft size={20} /></button>
          <button className={styles.carouselArrow} type="button" aria-label="Next testimonial" onClick={() => setUgcIndex((current) => (current + 1) % ugcReviews.length)}><ArrowRight size={20} /></button>
        </div>
        <div className={styles.ugcGrid}>
          {visibleUgc.map((review, index) => (
            <motion.article key={`${review.name}-${ugcIndex}`} className={styles.ugcCard} initial={{ opacity: 0, x: 18 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.35, delay: index * 0.05 }}>
              <div className={styles.ugcPhoto}><span>{review.name.slice(0, 1)}</span></div>
              <div className={styles.ugcContent}>
                <Stars />
                <p>"{review.quote}"</p>
                <strong>{review.name}</strong>
                <small>{review.location} | Verified Purchase</small>
              </div>
            </motion.article>
          ))}
        </div>
      </section>

      <section className={styles.writtenReviews}>
        {writtenReviews.map((review) => (
          <article key={review.name} className={styles.reviewCard}>
            <Stars />
            <div className={styles.avatar}>{review.name.slice(0, 1)}</div>
            <strong>{review.name}</strong>
            <span>{review.location}</span>
            <p>"{review.quote}"</p>
            <small>Verified Purchase</small>
          </article>
        ))}
      </section>

      <section className={styles.faq} id="faq">
        <div className={styles.sectionHeader}>
          <span>Questions answered</span>
          <h2>Everything before you brush.</h2>
        </div>
        <div className={styles.faqList}>
          {faqs.map((faq, index) => {
            const isOpen = openFaq === index;
            return (
              <article className={styles.faqItem} key={faq.q}>
                <button type="button" onClick={() => setOpenFaq(isOpen ? -1 : index)}>{faq.q}<ChevronDown className={isOpen ? styles.chevronOpen : ""} size={20} /></button>
                <AnimatePresence initial={false}>
                  {isOpen ? (
                    <motion.p initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.28 }}>{faq.a}</motion.p>
                  ) : null}
                </AnimatePresence>
              </article>
            );
          })}
        </div>
      </section>

      <section className={styles.guarantee}>
        <div className={styles.seal}><Check size={34} /></div>
        <div>
          <span>30-day promise</span>
          <h2>Glass Skin or Your Money Back</h2>
          <p>We are so confident in the Lymphatic Brush that we offer a 30-day money-back guarantee. If you do not see visible improvements in puffiness, jaw definition, or overall glow, we will refund you in full. No questions asked.</p>
        </div>
      </section>

      <section className={styles.finalCta}>
        <span>Only 12 left in stock</span>
        <h2>Ready to Transform Your Face?</h2>
        <p>Join 27,000+ customers already glowing.</p>
        <div className={styles.heroActions}>
          <AddToCartButton />
          <a className={styles.secondaryButton} href="#top">Continue Shopping</a>
        </div>
        <div className={styles.trustGrid}>
          <span><Check size={16} /> Free shipping on $50+</span>
          <span><Check size={16} /> Ships within 24 hours</span>
          <span><Check size={16} /> 30-day returns</span>
        </div>
      </section>

      <footer className={styles.footer}>
        <div>
          <a className={styles.logo} href="#top">aliaa<span>tm</span></a>
          <p>Clean skincare tools for sculpted, glass-skin rituals.</p>
          <div className={styles.socials}><a href="#">Instagram</a><a href="#">TikTok</a><a href="#">Pinterest</a></div>
        </div>
        <div className={styles.footerLinks}>
          <a href="#results">Results</a>
          <a href="#how">How it works</a>
          <a href="#faq">FAQ</a>
          <a href="/privacy-policy">Privacy</a>
          <a href="/refund-policy">Returns</a>
        </div>
        <form className={styles.newsletter}>
          <label htmlFor="aliaa-email">Glow notes</label>
          <div><input id="aliaa-email" type="email" placeholder="Email address" /><button type="submit">Join</button></div>
          <small>Visa | Mastercard | Amex | PayPal</small>
        </form>
      </footer>

      <aside className={styles.stickyCta} aria-label="Sticky add to cart">
        <AddToCartButton compact />
      </aside>
    </main>
  );
}
