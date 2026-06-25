import type { VercelRequest, VercelResponse } from '@vercel/node';
import nodemailer from 'nodemailer';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { name, company, email, phone, teamSize, message } = req.body as {
    name: string; company: string; email: string;
    phone?: string; teamSize: string; message: string;
  };

  if (!name || !company || !email || !message) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT ?? 587),
    secure: process.env.SMTP_SECURE === 'true',
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    },
  });

  await transporter.sendMail({
    from: `"Vantro Sales" <${process.env.SMTP_USER}>`,
    to: 'hello@vantro.ai',
    replyTo: email,
    subject: `Enterprise inquiry — ${company}`,
    text: [
      `Name: ${name}`,
      `Company: ${company}`,
      `Email: ${email}`,
      `Phone: ${phone || 'Not provided'}`,
      `Team size: ${teamSize}`,
      `Message:\n${message}`,
    ].join('\n'),
    html: `
      <h2>Enterprise inquiry — ${company}</h2>
      <table cellpadding="8" style="border-collapse:collapse;font-family:sans-serif;font-size:14px">
        <tr><td><b>Name</b></td><td>${name}</td></tr>
        <tr><td><b>Company</b></td><td>${company}</td></tr>
        <tr><td><b>Email</b></td><td><a href="mailto:${email}">${email}</a></td></tr>
        <tr><td><b>Phone</b></td><td>${phone || '—'}</td></tr>
        <tr><td><b>Team size</b></td><td>${teamSize}</td></tr>
        <tr><td valign="top"><b>Message</b></td><td>${message.replace(/\n/g, '<br>')}</td></tr>
      </table>
    `,
  });

  return res.status(200).json({ ok: true });
}
