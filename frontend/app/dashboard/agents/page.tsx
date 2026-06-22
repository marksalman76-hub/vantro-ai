'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface AgentMeta {
  id: string; name: string; category: string; role: string;
  architecture: string; hitl_level: string; min_package: string;
  credit_estimate: number; capabilities: string[]; unlocked: boolean;
}
interface AgentListResponse { tier: string; total: number; agents: AgentMeta[]; }
interface JobResult { job_id: string; agent_id: string; agent_name: string; status: string; hitl_level: string; credits_used: number; output: string | null; error_message: string | null; }
interface HistoryJob { id: string; agent_id: string; agent_name: string; status: string; hitl_level: string; credits_used: number; error_message: string | null; created_at: string | null; completed_at: string | null; }
interface Integration { key: string; name: string; icon: string; providers: string[]; agents: string[]; highRisk: string[]; connected: boolean; status: 'connected' | 'not_connected' | 'error'; }

const DEFAULT_INTEGRATIONS: Integration[] = [
  { key:'email',     name:'Email',         icon:'✉',  providers:['Gmail','Outlook','Brevo'],                agents:['Email Reply Agent','Sales Agent'],               highRisk:['send email','bulk send'],             connected:false, status:'not_connected' },
  { key:'crm',       name:'CRM',           icon:'♟',  providers:['GoHighLevel','HubSpot','Salesforce'],     agents:['CRM Agent','Lead Generator'],                   highRisk:['create contact','update deal'],        connected:false, status:'not_connected' },
  { key:'store',     name:'Ecommerce',     icon:'🛒', providers:['Shopify','WooCommerce','BigCommerce'],    agents:['Ecommerce Agent','Analytics Agent'],             highRisk:['update product','change price'],       connected:false, status:'not_connected' },
  { key:'website',   name:'Website / CMS', icon:'🌐', providers:['WordPress','Webflow','Shopify CMS'],     agents:['Website Agent','SEO Agent'],                    highRisk:['publish page','deploy site'],          connected:false, status:'not_connected' },
  { key:'calendar',  name:'Calendar',      icon:'📅', providers:['Google Calendar','Outlook Calendar'],    agents:['Receptionist Agent','Sales Agent'],              highRisk:['book appointment'],                    connected:false, status:'not_connected' },
  { key:'sms',       name:'SMS / Phone',   icon:'💬', providers:['Twilio','ClickSend'],                    agents:['Receptionist Agent','Customer Success Agent'],   highRisk:['send SMS','bulk SMS'],                 connected:false, status:'not_connected' },
  { key:'social',    name:'Social Media',  icon:'📲', providers:['Meta','Instagram','TikTok','LinkedIn'],  agents:['Social Media Agent','UGC Media Agent'],          highRisk:['publish post','send DM'],              connected:false, status:'not_connected' },
  { key:'ads',       name:'Ad Accounts',   icon:'📢', providers:['Meta Ads','Google Ads','TikTok Ads'],   agents:['Ads Optimisation Agent','Marketing Agent'],      highRisk:['launch campaign','increase budget'],   connected:false, status:'not_connected' },
  { key:'analytics', name:'Analytics',     icon:'📊', providers:['GA4','Search Console','Meta Pixel'],    agents:['Analytics Agent','SEO Agent'],                   highRisk:[],                                      connected:false, status:'not_connected' },
];

const CAT_COLOR: Record<string,string> = {
  Executive:'bg-amber-500/10 text-amber-400 border-amber-500/20', Strategy:'bg-violet-500/10 text-violet-400 border-violet-500/20',
  Research:'bg-purple-500/10 text-purple-400 border-purple-500/20', Sales:'bg-blue-500/10 text-blue-400 border-blue-500/20',
  Marketing:'bg-pink-500/10 text-pink-400 border-pink-500/20', Media:'bg-orange-500/10 text-orange-400 border-orange-500/20',
  Digital:'bg-indigo-500/10 text-indigo-400 border-indigo-500/20', Support:'bg-teal-500/10 text-teal-400 border-teal-500/20',
  Operations:'bg-gray-500/10 text-gray-300 border-gray-500/20',
};
const HITL: Record<string,{label:string;color:string;tip:string}> = {
  'HITL-0':{label:'Autonomous', color:'bg-green-500/10 text-green-400 border-green-500/20',   tip:'Runs without approval'},
  'HITL-1':{label:'Review',     color:'bg-blue-500/10 text-blue-400 border-blue-500/20',      tip:'Output for your review'},
  'HITL-2':{label:'Approval',   color:'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',tip:'You approve before external action'},
  'HITL-3':{label:'Owner gate', color:'bg-red-500/10 text-red-400 border-red-500/20',         tip:'Admin approval required'},
};
const TIER_BADGE: Record<string,string> = {
  starter:'bg-green-500/10 text-green-400 border-green-500/20', growth:'bg-blue-500/10 text-blue-400 border-blue-500/20',
  business:'bg-violet-500/10 text-violet-400 border-violet-500/20', enterprise:'bg-amber-500/10 text-amber-400 border-amber-500/20',
};
const TIER_ORDER = ['starter','growth','business','enterprise'];
const POLL_MS = 2500;

function StatusBadge({active}:{active:boolean}) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider ${active?'border-emerald-500/30 bg-emerald-500/10 text-emerald-400':'border-rose-500/30 bg-rose-500/10 text-rose-400'}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${active?'bg-emerald-400 animate-pulse':'bg-rose-400'}`}/>
      {active?'ACTIVE':'INACTIVE'}
    </span>
  );
}

function JobOutputModal({job,onDismiss}:{job:JobResult;onDismiss:()=>void}) {
  const lines=(job.output??'').split('\n');
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <div>
            <p className="font-semibold text-white">{job.agent_name}</p>
            <p className="text-xs text-gray-500 mt-0.5">{job.credits_used} credits · {job.job_id.slice(0,8)}</p>
          </div>
          <button onClick={onDismiss} className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-white hover:bg-gray-800">✕</button>
        </div>
        <div className="flex-1 overflow-y-auto px-6 py-5">
          {job.status==='failed' ? (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
              <p className="text-red-400 text-sm font-medium mb-1">Execution failed</p>
              <p className="text-red-400/70 text-xs">{job.error_message}</p>
            </div>
          ) : job.status==='pending_approval' ? (
            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4">
              <p className="text-yellow-400 text-sm font-medium mb-1">Awaiting admin approval</p>
              <p className="text-yellow-400/70 text-xs">This agent requires owner approval before it executes.</p>
            </div>
          ) : (
            <div className="space-y-1">
              {lines.map((line,i) => {
                if(/^#{1,3}\s/.test(line)) return <p key={i} className="font-bold text-white text-sm mt-4 mb-1">{line.replace(/^#+\s/,'')}</p>;
                if(/^[-*]\s|^\d+\.\s/.test(line)) return <p key={i} className="text-gray-300 text-sm ml-3 leading-relaxed">{line}</p>;
                if(!line.trim()) return <div key={i} className="h-2"/>;
                return <p key={i} className="text-gray-300 text-sm leading-relaxed">{line}</p>;
              })}
            </div>
          )}
        </div>
        <div className="px-6 py-4 border-t border-gray-800 flex justify-between">
          <button onClick={()=>navigator.clipboard?.writeText(job.output??'')} className="text-xs text-gray-500 hover:text-white">Copy output</button>
          <button onClick={onDismiss} className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white text-xs font-medium rounded-lg">Close</button>
        </div>
      </div>
    </div>
  );
}

function RunModal({agent,onClose,onJobCreated}:{agent:AgentMeta;onClose:()=>void;onJobCreated:(id:string,name:string)=>void}) {
  const [prompt,setPrompt]=useState('');
  const [submitting,setSubmitting]=useState(false);
  const [error,setError]=useState('');
  const h=HITL[agent.hitl_level]??HITL['HITL-1'];
  const ref=useRef<HTMLTextAreaElement>(null);
  useEffect(()=>{ref.current?.focus();},[]);
  const submit=async()=>{
    if(!prompt.trim())return;
    const token=localStorage.getItem('token');
    if(!token)return;
    setSubmitting(true);setError('');
    try{
      const res=await fetch(`/api/agents/${agent.id}/run`,{method:'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},body:JSON.stringify({prompt:prompt.trim()})});
      const json=await res.json();
      if(!res.ok){setError(json.detail||'Submission failed');return;}
      onJobCreated(json.job_id,json.agent_name);
    }catch{setError('Network error');}
    finally{setSubmitting(false);}
  };
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-xl shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <div>
            <p className="font-semibold text-white">{agent.name}</p>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${h.color}`}>{h.label}</span>
              <span className="text-[10px] text-gray-500">{h.tip}</span>
            </div>
          </div>
          <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-white hover:bg-gray-800">✕</button>
        </div>
        <div className="px-6 py-5">
          <p className="text-xs text-gray-500 mb-3">~{agent.credit_estimate} credits · {agent.category}</p>
          <textarea ref={ref} value={prompt} onChange={e=>setPrompt(e.target.value)} rows={6}
            placeholder={`Describe what you want ${agent.name} to do. Be specific — the more context, the better.`}
            className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 resize-none focus:outline-none focus:border-violet-500 leading-relaxed"/>
          {error&&<p className="text-red-400 text-xs mt-2">{error}</p>}
          {agent.hitl_level==='HITL-3'&&<div className="mt-3 bg-red-500/5 border border-red-500/20 rounded-lg px-3 py-2"><p className="text-red-400 text-xs">Requires admin approval before execution.</p></div>}
        </div>
        <div className="px-6 pb-5 flex gap-3">
          <button onClick={submit} disabled={!prompt.trim()||submitting} className="flex-1 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 text-white text-sm font-medium px-4 py-2.5 rounded-xl transition-colors">
            {submitting?'Submitting…':agent.hitl_level==='HITL-3'?'Submit for approval':'Run agent'}
          </button>
          <button onClick={onClose} className="px-4 py-2.5 text-sm text-gray-400 hover:text-white border border-gray-700 rounded-xl">Cancel</button>
        </div>
      </div>
    </div>
  );
}

function IntegrationsPanel({integrations,onConnect,onDisconnect}:{integrations:Integration[];onConnect:(k:string)=>void;onDisconnect:(k:string)=>void}) {
  const [expanded,setExpanded]=useState<string|null>(null);
  const connected=integrations.filter(i=>i.connected).length;
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="font-semibold text-white">Integrations</h2>
          <p className="text-gray-500 text-xs mt-0.5">Connect your tools so agents can act on live data</p>
        </div>
        <span className="text-xs text-gray-600 bg-gray-800 px-2.5 py-1 rounded-full border border-gray-700">{connected}/{integrations.length} connected</span>
      </div>
      <div className="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-9 gap-2">
        {integrations.map(intg=>(
          <button key={intg.key} onClick={()=>setExpanded(expanded===intg.key?null:intg.key)}
            className={`relative flex flex-col items-center gap-1.5 p-3 rounded-xl border text-center transition-all ${intg.connected?'border-emerald-500/40 bg-emerald-500/5 hover:bg-emerald-500/10':expanded===intg.key?'border-violet-500/40 bg-violet-500/5':'border-gray-800 bg-gray-800/30 hover:border-gray-700'}`}>
            {intg.connected&&<span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"/>}
            <span className="text-xl">{intg.icon}</span>
            <span className="text-[10px] font-medium text-gray-300 leading-tight">{intg.name}</span>
            <span className={`text-[9px] font-bold ${intg.connected?'text-emerald-400':'text-gray-600'}`}>{intg.connected?'● ON':'○ OFF'}</span>
          </button>
        ))}
      </div>
      {expanded&&(()=>{
        const intg=integrations.find(i=>i.key===expanded)!;
        return (
          <div className="mt-4 bg-gray-800/60 border border-gray-700 rounded-xl p-4 flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">{intg.icon}</span>
                <p className="font-semibold text-white text-sm">{intg.name}</p>
                <StatusBadge active={intg.connected}/>
              </div>
              <p className="text-xs text-gray-500 mb-1"><span className="text-gray-400">Providers:</span> {intg.providers.join(', ')}</p>
              <p className="text-xs text-gray-500 mb-2"><span className="text-gray-400">Used by:</span> {intg.agents.join(', ')}</p>
              {intg.highRisk.length>0&&<div className="flex flex-wrap gap-1">{intg.highRisk.map(a=><span key={a} className="text-[10px] px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">⚠ {a}</span>)}</div>}
            </div>
            <div className="flex flex-col gap-2 shrink-0">
              {intg.connected?(
                <>
                  <button onClick={()=>{onDisconnect(intg.key);setExpanded(null);}} className="px-3 py-1.5 rounded-lg text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20">Disconnect</button>
                  <button className="px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-700 text-gray-300 hover:bg-gray-600">Test</button>
                </>
              ):<button onClick={()=>{onConnect(intg.key);setExpanded(null);}} className="px-3 py-1.5 rounded-lg text-xs font-medium bg-violet-600 text-white hover:bg-violet-500">Connect</button>}
              <button onClick={()=>setExpanded(null)} className="px-3 py-1.5 rounded-lg text-xs text-gray-500 hover:text-white border border-gray-700">Close</button>
            </div>
          </div>
        );
      })()}
    </div>
  );
}

function RunTaskPanel({agents,onJobCreated}:{agents:AgentMeta[];onJobCreated:(id:string,name:string)=>void}) {
  const unlocked=agents.filter(a=>a.unlocked);
  const [selectedId,setSelectedId]=useState(unlocked[0]?.id??'');
  const [task,setTask]=useState('Create a client-specific deliverable using the saved business profile, selected agent, current offer, target audience, and goals.');
  const [submitting,setSubmitting]=useState(false);
  const [error,setError]=useState('');
  const sel=agents.find(a=>a.id===selectedId);
  const run=async()=>{
    if(!task.trim()||!selectedId)return;
    const token=localStorage.getItem('token');
    if(!token)return;
    setSubmitting(true);setError('');
    try{
      const res=await fetch(`/api/agents/${selectedId}/run`,{method:'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},body:JSON.stringify({prompt:task.trim()})});
      const json=await res.json();
      if(!res.ok){setError(json.detail||'Failed');return;}
      onJobCreated(json.job_id,json.agent_name);
    }catch{setError('Network error');}
    finally{setSubmitting(false);}
  };
  const ICONS:Record<string,string>={research:'⌕',copy:'✎',ugc:'▣',image:'▧',crm:'♟',email:'✉',analytic:'↗',influencer:'★',seo:'◎',social:'◈',sales:'◆',reception:'☎',content:'✍',strategy:'◉'};
  const iconFor=(name:string)=>{const n=name.toLowerCase();return Object.entries(ICONS).find(([k])=>n.includes(k))?.[1]??'◦';};
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
      <div className="flex items-start gap-3 mb-5">
        <div className="w-8 h-8 rounded-lg bg-violet-600/20 border border-violet-500/30 flex items-center justify-center text-violet-400 font-bold text-xs shrink-0">01</div>
        <div>
          <h2 className="font-semibold text-white">Run AI Agent</h2>
          <p className="text-gray-500 text-xs mt-0.5">Select an active agent, describe your task, and launch governed execution</p>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-5">
        <div>
          <p className="text-xs font-medium text-gray-400 mb-2 flex items-center justify-between">
            Active agents <span className="text-violet-400 font-semibold">{unlocked.length}/27</span>
          </p>
          {unlocked.length===0?(
            <div className="text-center py-8 border border-dashed border-gray-800 rounded-xl">
              <p className="text-gray-600 text-xs mb-2">No agents unlocked</p>
              <Link href="/pricing" className="text-violet-400 text-xs">Upgrade plan →</Link>
            </div>
          ):(
            <div className="space-y-1.5 max-h-72 overflow-y-auto pr-1">
              {unlocked.map(agent=>{
                const active=agent.id===selectedId;
                return (
                  <button key={agent.id} onClick={()=>setSelectedId(agent.id)}
                    className={`w-full text-left flex items-center gap-2.5 px-3 py-2 rounded-xl border text-xs transition-all ${active?'border-violet-500/40 bg-violet-600/10 text-violet-300':'border-gray-800 bg-gray-800/30 text-gray-400 hover:border-gray-700 hover:text-white'}`}>
                    <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[9px] shrink-0 font-bold ${active?'bg-violet-600 text-white':'border border-gray-600 text-gray-600'}`}>{active?'✓':iconFor(agent.name)}</span>
                    <span className="truncate font-medium">{agent.name}</span>
                    {active&&<StatusBadge active={true}/>}
                  </button>
                );
              })}
            </div>
          )}
        </div>
        <div className="flex flex-col gap-3">
          <div>
            <p className="text-xs font-medium text-gray-400 mb-2">Task description</p>
            <textarea value={task} onChange={e=>setTask(e.target.value)} rows={8}
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 resize-none focus:outline-none focus:border-violet-500 leading-relaxed"/>
          </div>
          {sel&&(
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${CAT_COLOR[sel.category]||''}`}>{sel.category}</span>
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${HITL[sel.hitl_level]?.color||''}`}>{HITL[sel.hitl_level]?.label}</span>
              <span className="text-[10px] text-gray-500">~{sel.credit_estimate} credits</span>
            </div>
          )}
          {error&&<p className="text-red-400 text-xs">{error}</p>}
          <button onClick={run} disabled={submitting||!task.trim()||!selectedId}
            className="w-full bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 disabled:opacity-40 text-white font-semibold py-3 rounded-xl text-sm transition-all shadow-lg shadow-violet-500/20">
            {submitting?'Launching…':sel?.hitl_level==='HITL-3'?'Submit for approval':'▶  Launch execution'}
          </button>
        </div>
      </div>
    </div>
  );
}

function ExecutionHistory({onView}:{onView:(id:string)=>void}) {
  const [jobs,setJobs]=useState<HistoryJob[]>([]);
  const [loading,setLoading]=useState(true);
  useEffect(()=>{
    const token=localStorage.getItem('token');
    if(!token)return;
    fetch('/api/agents/jobs',{headers:{Authorization:`Bearer ${token}`}})
      .then(r=>r.ok?r.json():null).then(d=>{if(d?.jobs)setJobs(d.jobs.slice(0,15));}).finally(()=>setLoading(false));
  },[]);
  const S:Record<string,string>={completed:'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',running:'text-blue-400 bg-blue-500/10 border-blue-500/20',pending:'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',pending_approval:'text-orange-400 bg-orange-500/10 border-orange-500/20',failed:'text-red-400 bg-red-500/10 border-red-500/20',rejected:'text-red-400 bg-red-500/10 border-red-500/20'};
  if(loading)return <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 text-center text-gray-600 text-sm">Loading…</div>;
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
        <h2 className="font-semibold text-white text-sm">Execution History</h2>
        <span className="text-xs text-gray-600">{jobs.length} jobs</span>
      </div>
      {jobs.length===0?(
        <p className="text-center text-gray-600 text-sm py-8">No jobs yet — run your first task above.</p>
      ):(
        <div className="divide-y divide-gray-800/60">
          {jobs.map(job=>(
            <div key={job.id} className="flex items-center gap-4 px-6 py-3 hover:bg-gray-800/30 transition-colors">
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white font-medium truncate">{job.agent_name}</p>
                <p className="text-xs text-gray-600">{job.created_at?new Date(job.created_at).toLocaleString():'—'}</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold ${S[job.status]||'text-gray-400 bg-gray-800 border-gray-700'}`}>{job.status.replace(/_/g,' ')}</span>
                {job.credits_used>0&&<span className="text-[10px] text-gray-600">{job.credits_used}cr</span>}
                {job.status==='completed'&&<button onClick={()=>onView(job.id)} className="text-[10px] text-violet-400 hover:text-violet-300 font-medium">View →</button>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function AgentCatalogue({agents,onRun}:{agents:AgentMeta[];onRun:(a:AgentMeta)=>void}) {
  const [catFilter,setCatFilter]=useState('All');
  const [showLocked,setShowLocked]=useState(false);
  const [expanded,setExpanded]=useState<string|null>(null);
  const cats=['All',...Array.from(new Set(agents.map(a=>a.category)))];
  const filtered=agents.filter(a=>{
    if(catFilter!=='All'&&a.category!==catFilter)return false;
    if(!showLocked&&!a.unlocked)return false;
    return true;
  });
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div><h2 className="font-semibold text-white">Agent Catalogue</h2><p className="text-gray-500 text-xs mt-0.5">All 27 agents — click to expand and run</p></div>
        <button onClick={()=>setShowLocked(v=>!v)} className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${showLocked?'border-violet-500/40 text-violet-400 bg-violet-500/10':'border-gray-700 text-gray-500 hover:text-white'}`}>{showLocked?'Hide locked':'Show locked'}</button>
      </div>
      <div className="flex flex-wrap gap-1.5 mb-5">
        {cats.map(c=><button key={c} onClick={()=>setCatFilter(c)} className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${catFilter===c?'bg-violet-600 text-white':'bg-gray-800 border border-gray-700 text-gray-400 hover:text-white'}`}>{c}</button>)}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
        {filtered.map(agent=>{
          const h=HITL[agent.hitl_level]??HITL['HITL-1'];
          const isExp=expanded===agent.id;
          return (
            <div key={agent.id} className={`rounded-xl border p-4 cursor-pointer transition-all ${agent.unlocked?'bg-gray-800/50 border-gray-700 hover:border-gray-600':'bg-gray-900/30 border-gray-800/40 opacity-50'}`} onClick={()=>setExpanded(isExp?null:agent.id)}>
              <div className="flex items-start gap-2 mb-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 flex-wrap mb-1.5">
                    <p className="text-xs font-semibold text-white">{agent.name}</p>
                    {!agent.unlocked&&<span className="text-xs">🔒</span>}
                    {agent.unlocked&&<StatusBadge active={true}/>}
                  </div>
                  <div className="flex flex-wrap gap-1">
                    <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded border ${CAT_COLOR[agent.category]||''}`}>{agent.category}</span>
                    <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded border ${h.color}`} title={h.tip}>{h.label}</span>
                  </div>
                </div>
                <span className="text-[10px] text-gray-600 shrink-0">~{agent.credit_estimate}cr</span>
              </div>
              <p className="text-gray-500 text-[11px] leading-relaxed line-clamp-2">{agent.role}</p>
              {isExp&&(
                <div className="mt-3 pt-3 border-t border-gray-700">
                  {agent.capabilities.length>0&&<div className="flex flex-wrap gap-1 mb-3">{agent.capabilities.map(c=><span key={c} className="text-[10px] px-1.5 py-0.5 rounded bg-gray-700 text-gray-300 border border-gray-600">{c}</span>)}</div>}
                  {agent.unlocked?(
                    <button onClick={e=>{e.stopPropagation();onRun(agent);}} className="w-full bg-violet-600/20 hover:bg-violet-600/30 border border-violet-500/30 text-violet-400 text-[11px] font-medium px-3 py-1.5 rounded-lg transition-colors">Run this agent →</button>
                  ):(
                    <Link href="/pricing" onClick={e=>e.stopPropagation()} className="block w-full text-center bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-400 text-[11px] font-medium px-3 py-1.5 rounded-lg transition-colors">Upgrade to unlock</Link>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
      {filtered.length===0&&<p className="text-center text-gray-600 text-sm py-8">No agents match the current filters.</p>}
    </div>
  );
}

export default function DashboardAgentsPage() {
  const router=useRouter();
  const [data,setData]=useState<AgentListResponse|null>(null);
  const [loading,setLoading]=useState(true);
  const [integrations,setIntegrations]=useState<Integration[]>(DEFAULT_INTEGRATIONS);
  const [runningAgent,setRunningAgent]=useState<AgentMeta|null>(null);
  const [activeJob,setActiveJob]=useState<{jobId:string;agentName:string}|null>(null);
  const [jobResult,setJobResult]=useState<JobResult|null>(null);
  const [viewJobId,setViewJobId]=useState<string|null>(null);
  const pollRef=useRef<NodeJS.Timeout|null>(null);

  useEffect(()=>{
    try{const saved=localStorage.getItem('vantro_integrations');if(saved)setIntegrations(JSON.parse(saved));}catch{}
  },[]);

  useEffect(()=>{
    const token=localStorage.getItem('token');
    if(!token){router.push('/login');return;}
    fetch('/api/agents/all',{headers:{Authorization:`Bearer ${token}`}})
      .then(r=>r.ok?r.json():Promise.reject(r.status)).then(setData).catch(()=>router.push('/login')).finally(()=>setLoading(false));
  },[router]);

  const updateIntegrations=(updated:Integration[])=>{setIntegrations(updated);localStorage.setItem('vantro_integrations',JSON.stringify(updated));};

  useEffect(()=>{
    if(!activeJob){if(pollRef.current)clearInterval(pollRef.current);return;}
    const poll=async()=>{
      const token=localStorage.getItem('token');if(!token)return;
      try{
        const res=await fetch(`/api/agents/jobs/${activeJob.jobId}`,{headers:{Authorization:`Bearer ${token}`}});
        if(!res.ok)return;
        const job:JobResult=await res.json();
        if(['completed','failed','pending_approval','rejected'].includes(job.status)){setJobResult(job);setActiveJob(null);if(pollRef.current)clearInterval(pollRef.current);}
      }catch{}
    };
    poll();pollRef.current=setInterval(poll,POLL_MS);
    return()=>{if(pollRef.current)clearInterval(pollRef.current);};
  },[activeJob]);

  useEffect(()=>{
    if(!viewJobId)return;
    const token=localStorage.getItem('token');if(!token)return;
    fetch(`/api/agents/jobs/${viewJobId}`,{headers:{Authorization:`Bearer ${token}`}}).then(r=>r.ok?r.json():null).then(j=>{if(j)setJobResult(j);setViewJobId(null);});
  },[viewJobId]);

  const handleJobCreated=useCallback((jobId:string,agentName:string)=>{setRunningAgent(null);setActiveJob({jobId,agentName});},[]);

  if(loading)return <div className="min-h-screen bg-gray-950 flex items-center justify-center"><div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"/></div>;
  if(!data)return null;

  const tier=data.tier;
  const tierIdx=TIER_ORDER.indexOf(tier);
  const unlockedCount=data.agents.filter(a=>a.unlocked).length;
  const connectedCount=integrations.filter(i=>i.connected).length;

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {runningAgent&&<RunModal agent={runningAgent} onClose={()=>setRunningAgent(null)} onJobCreated={handleJobCreated}/>}
      {jobResult&&<JobOutputModal job={jobResult} onDismiss={()=>setJobResult(null)}/>}
      {activeJob&&(
        <div className="fixed bottom-6 right-6 z-40 bg-gray-900 border border-violet-500/30 rounded-2xl px-5 py-3.5 shadow-2xl flex items-center gap-3">
          <div className="w-4 h-4 border-2 border-violet-500 border-t-transparent rounded-full animate-spin shrink-0"/>
          <div><p className="text-white text-xs font-semibold">{activeJob.agentName} running…</p><p className="text-gray-500 text-[10px]">Results appear automatically</p></div>
        </div>
      )}
      <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between sticky top-0 bg-gray-950/95 backdrop-blur z-30">
        <Link href="/" className="flex items-center gap-2">
          <span className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-xs">V</span>
          <span className="font-bold">Vantro<span className="text-violet-400">.ai</span></span>
        </Link>
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-gray-400 hover:text-white text-sm">Dashboard</Link>
          <button onClick={()=>{localStorage.removeItem('token');router.push('/login');}} className="text-gray-400 hover:text-white text-sm">Sign out</button>
        </div>
      </nav>
      <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold">AI Agent Workspace</h1>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border capitalize ${TIER_BADGE[tier]||'border-gray-700 text-gray-400'}`}>{tier} plan</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-500 flex-wrap">
              <span><span className="text-emerald-400 font-semibold">{unlockedCount}</span> agents active</span>
              <span>·</span>
              <span><span className="text-blue-400 font-semibold">{connectedCount}</span> integrations connected</span>
              <span>·</span>
              <StatusBadge active={unlockedCount>0}/>
            </div>
          </div>
          {tierIdx<TIER_ORDER.length-1&&<Link href="/pricing" className="bg-violet-600 hover:bg-violet-500 text-white text-sm px-5 py-2.5 rounded-xl font-medium transition-colors">Unlock more →</Link>}
        </div>

        <IntegrationsPanel integrations={integrations}
          onConnect={key=>updateIntegrations(integrations.map(i=>i.key===key?{...i,connected:true,status:'connected' as const}:i))}
          onDisconnect={key=>updateIntegrations(integrations.map(i=>i.key===key?{...i,connected:false,status:'not_connected' as const}:i))}/>

        <RunTaskPanel agents={data.agents} onJobCreated={handleJobCreated}/>

        <ExecutionHistory onView={id=>setViewJobId(id)}/>

        <AgentCatalogue agents={data.agents} onRun={setRunningAgent}/>

        {tierIdx<TIER_ORDER.length-1&&(
          <div className="bg-violet-950/30 border border-violet-500/20 rounded-2xl p-6 text-center">
            <p className="text-white font-semibold mb-1">Unlock more powerful agents</p>
            <p className="text-gray-400 text-sm mb-4">Upgrade to access UGC Media, Ads Optimisation, Finance Admin, and the Head Agent CEO.</p>
            <Link href="/pricing" className="inline-block bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium px-6 py-2.5 rounded-xl transition-colors">View upgrade options</Link>
          </div>
        )}
      </div>
    </div>
  );
}
