\# Provider Selection Matrix



\## Purpose

This matrix tracks which external providers can power real-world execution for the Ecommerce AI Agent Platform.



The system must stay provider-flexible, globally usable, white-label ready, and owner-governed.



\---



\# Core Selection Rules



\## Provider Must Support

\- API access or reliable automation pathway

\- Commercial usage

\- White-label/client-safe delivery

\- High-quality outputs

\- Global market support

\- Secure credential handling

\- Scalable usage

\- Clear pricing

\- Quality consistency



\## Provider Must Not Expose

\- Internal prompts

\- Backend configuration

\- API keys

\- Hidden scoring logic

\- Other client data

\- Internal workflow structure



\---



\# Provider Categories



| Category | Primary Use | Candidate Providers | Selection Status |

|---|---|---|---|

| UGC Video / Avatar | Realistic multilingual UGC videos | HeyGen, Creatify, Synthesia, Higgsfield, Runway, Kling, Tavus | Under review |

| Voice / Audio | Natural multilingual voiceovers | ElevenLabs, PlayHT, Azure Speech, Google Speech | Under review |

| Product Images | Ecommerce product photography and lifestyle scenes | Claid, Photoroom, Pebblely, Nightjar, Pixelcut, Midjourney, OpenAI image generation | Under review |

| Shopify Execution | Product/page creation | Shopify Admin API | Preferred |

| Website / Landing Pages | White-label page generation | 10Web-style internal builder, custom Next.js builder, Webflow API | Under review |

| Influencer Outreach | Creator tracking and outreach | Modash, Upfluence, Shopify Collabs, manual CRM/email adapter | Under review |

| Email Marketing | Email campaigns and flows | Klaviyo, Brevo, Omnisend, Mailchimp | Under review |

| Analytics | Ecommerce and ad reporting | Shopify Analytics, GA4, Meta Ads API, TikTok Ads API, Triple Whale | Under review |

| CRM / Support | Customer service and CRM actions | Gorgias, Zendesk, Intercom, HubSpot | Under review |

| Automation | Workflow execution | n8n, Make, custom backend workers | Under review |



\---



\# UGC Video Provider Requirements



Must support:

\- Realistic human avatars or creator-style video

\- Multiple ages

\- Multiple genders

\- Multiple ethnicities

\- Multiple languages

\- Region-specific accents

\- Accurate lip sync

\- Smooth facial movement

\- No lag or distortion

\- Commercial ad usage

\- API access or controlled generation workflow



Reject provider if:

\- Lip sync is weak

\- Output looks uncanny

\- Motion is distorted

\- Language support is limited

\- API/control layer is weak

\- Commercial usage is unclear



\---



\# Product Image Provider Requirements



Must support:

\- Accurate product preservation

\- Studio product images

\- Lifestyle scenes

\- Ecommerce-ready resolution

\- Marketplace-safe composition

\- Brand-consistent scenes

\- Batch or API workflow

\- Low artefact rate



Reject provider if:

\- Product shape changes

\- Labels are hallucinated

\- Hands or people distort badly

\- Output looks generic

\- Resolution is too low

\- Commercial usage is unclear



\---



\# Shopify Provider Direction



Preferred path:

\- Shopify Admin API

\- Draft product creation first

\- Product title, body HTML, SEO metadata, price, tags, images

\- Owner/client approval before publishing live



Reason:

Shopify Admin GraphQL API supports product creation with attributes, options, and media, using the required product write access scope.



\---



\# Email Provider Direction



Possible paths:

\- Klaviyo for ecommerce flows

\- Brevo for cost-effective campaigns

\- Omnisend for ecommerce automations

\- Mailchimp for broad SMB use



Selection should depend on:

\- Client package

\- Region

\- Integration needs

\- Pricing

\- API support

\- Deliverability



\---



\# Approval-Gated Provider Actions



Owner approval required before:

\- Paid ad launch

\- Budget increase

\- Campaign scaling

\- Paid influencer deal

\- Commission agreement

\- Usage rights contract

\- Large product seeding

\- Large supplier order

\- Large refund batch



\---



\# Current Decision



Do not hardwire one provider yet.



Next build should keep adapters provider-flexible while preparing the first real provider integration path.



Recommended first real integration:

1\. Shopify draft product/page creation

2\. UGC/video provider selection

3\. Product image provider selection

4\. Email/influencer outreach adapter

5\. Analytics reporting adapter

