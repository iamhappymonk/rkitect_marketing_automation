// Vercel Edge / Node serverless function — POST /api/contact
// Uses Resend to send 2 emails:
//   1) To founder + cc accounts@happymonk.co with the full brief
//   2) Auto-reply to submitter
//
// Required env vars (set in Vercel project settings):
//   RESEND_API_KEY      — Resend API key
//   CONTACT_TO_EMAIL    — Optional. Defaults to bhavish@rkitect.ai
//   CONTACT_CC_EMAIL    — Optional. Defaults to accounts@happymonk.co
//   CONTACT_FROM_EMAIL  — Optional. Defaults to no-reply@rkitect.ai (must be a verified Resend domain)

export const config = { runtime: 'nodejs' };

type Body = {
  name?: string;
  email?: string;
  practice?: string;
  city?: string;
  channel?: string;
  brief?: string;
};

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export default async function handler(req: Request): Promise<Response> {
  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  let body: Body;
  try {
    body = (await req.json()) as Body;
  } catch {
    return new Response('Invalid JSON', { status: 400 });
  }

  const name = (body.name || '').trim().slice(0, 200);
  const email = (body.email || '').trim().slice(0, 200);
  const practice = (body.practice || '').trim().slice(0, 200);
  const city = (body.city || '').trim().slice(0, 200);
  const channel = (body.channel || 'Either').trim().slice(0, 50);
  const brief = (body.brief || '').trim().slice(0, 500);

  if (!name || !email || !brief) {
    return new Response('Missing required fields', { status: 400 });
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return new Response('Invalid email', { status: 400 });
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    return new Response('RESEND_API_KEY missing in environment', { status: 500 });
  }

  const to = process.env.CONTACT_TO_EMAIL || 'bhavish@rkitect.ai';
  const cc = process.env.CONTACT_CC_EMAIL || 'accounts@happymonk.co';
  const from = process.env.CONTACT_FROM_EMAIL || 'no-reply@rkitect.ai';

  const safe = {
    name: escapeHtml(name),
    email: escapeHtml(email),
    practice: escapeHtml(practice),
    city: escapeHtml(city),
    channel: escapeHtml(channel),
    brief: escapeHtml(brief).replace(/\n/g, '<br>'),
  };

  const adminHtml = `
    <h2 style="font-family:Georgia,serif;margin:0 0 16px;">New brief — rkitect.ai</h2>
    <table style="font-family:system-ui,sans-serif;font-size:14px;border-collapse:collapse;">
      <tr><td style="padding:4px 12px 4px 0;color:#666;">Name</td><td>${safe.name}</td></tr>
      <tr><td style="padding:4px 12px 4px 0;color:#666;">Email</td><td>${safe.email}</td></tr>
      <tr><td style="padding:4px 12px 4px 0;color:#666;">Practice</td><td>${safe.practice || '—'}</td></tr>
      <tr><td style="padding:4px 12px 4px 0;color:#666;">City</td><td>${safe.city || '—'}</td></tr>
      <tr><td style="padding:4px 12px 4px 0;color:#666;">Preferred channel</td><td>${safe.channel}</td></tr>
    </table>
    <h3 style="font-family:system-ui,sans-serif;margin:24px 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:0.1em;color:#666;">Brief</h3>
    <p style="font-family:system-ui,sans-serif;font-size:14px;line-height:1.55;">${safe.brief}</p>
  `;

  const replyHtml = `
    <p style="font-family:Georgia,serif;font-size:16px;line-height:1.55;">Brief received.</p>
    <p style="font-family:system-ui,sans-serif;font-size:14px;line-height:1.55;">Bhavish will be in touch within 48 hours.</p>
    <p style="font-family:system-ui,sans-serif;font-size:13px;line-height:1.55;color:#666;">If urgent — WhatsApp +91 82961 33123 or email accounts@happymonk.co.</p>
    <p style="font-family:system-ui,sans-serif;font-size:12px;line-height:1.55;color:#999;margin-top:24px;">— rkitect.ai · Built by HappyMonk AI · Bengaluru, India</p>
  `;

  async function send(payload: Record<string, unknown>) {
    return fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  }

  try {
    const [adminRes, replyRes] = await Promise.all([
      send({
        from: `rkitect.ai <${from}>`,
        to: [to],
        cc: [cc],
        reply_to: email,
        subject: `New brief — ${name}${practice ? ' · ' + practice : ''}`,
        html: adminHtml,
      }),
      send({
        from: `rkitect.ai <${from}>`,
        to: [email],
        subject: 'Brief received — rkitect.ai',
        html: replyHtml,
      }),
    ]);

    if (!adminRes.ok) {
      const txt = await adminRes.text();
      return new Response(`Admin send failed: ${txt}`, { status: 502 });
    }
    // reply failure is non-fatal — admin email is the critical path
    if (!replyRes.ok) {
      console.warn('Auto-reply failed', await replyRes.text());
    }

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : 'unknown';
    return new Response(`Send error: ${msg}`, { status: 500 });
  }
}
