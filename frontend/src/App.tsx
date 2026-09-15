import { useEffect, useMemo, useState, type Dispatch, type SetStateAction } from 'react';
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { apiCall, clearAuthToken, getAuthToken, setAuthToken } from './api';

type Stage = 'auth'|'verify-email'|'two-factor'|'profile'|'search'|'diagnostic'|'learn';
type DiagnosticQuestion = { id:string; skill:string; question:string; options:string[] };
type AssessmentQuestion = { id:string; question:string; options:string[]; correct_answer:string };
type LessonSet = { id:string; stage:string; title:string; goal:string; explanation?:string; learning_goals?:string[]; milestones?:string[] };
type PracticeSet = { id:string; lessonTitle?:string; question?:string; choices?:string[]; correct_answer?:string; explanation?:string; hint?:string; skill_tag?:string; difficulty?:string };

type Lesson = { output?: { content?: Record<string, any> } };
type Practice = PracticeSet & { output?: { content?: { question?:string; choices?:string[]; correct_answer?:string; explanation?:string; hint?:string; skill_tag?:string; difficulty?:string } } };
type Research = { output?: { content?: { sources?: Array<{title:string;url:string;publisher?:string;summary?:string}> } } };

const initialStage: Stage = getAuthToken() ? 'search' : 'auth';

export default function App() {
  return <BrowserRouter><AppShell /></BrowserRouter>;
}

function AppShell() {
  const [stage,setStage] = useState<Stage>(initialStage);
  const [mode,setMode] = useState<'login'|'register'>('login');
  const [name,setName] = useState('');
  const [email,setEmail] = useState('');
  const [password,setPassword] = useState('');
  const [code,setCode] = useState('');
  const [devCode,setDevCode] = useState('');
  const [challenge,setChallenge] = useState('');
  const [goal,setGoal] = useState('');
  const [educationLevel,setEducationLevel] = useState('');
  const [preferredStyle,setPreferredStyle] = useState('Step-by-step explanations');
  const [mentorOpen,setMentorOpen] = useState(false);
  const [mentorMessage,setMentorMessage] = useState('');
  const [mentorReply,setMentorReply] = useState<any>(null);
  const [query,setQuery] = useState('');
  const [topics,setTopics] = useState<string[]>([]);
  const [topic,setTopic] = useState('');
  const [questions,setQuestions] = useState<DiagnosticQuestion[]>([]);
  const [answers,setAnswers] = useState<Record<string,string>>({});
  const [level,setLevel] = useState('beginner');
  const [diagnostic,setDiagnostic] = useState<any>(null);
  const [lesson,setLesson] = useState<Lesson|null>(null);
  const [lessonSets,setLessonSets] = useState<LessonSet[]>([]);
  const [lessonIndex,setLessonIndex] = useState(0);
  const [practice,setPractice] = useState<Practice|null>(null);
  const [practiceSets,setPracticeSets] = useState<PracticeSet[]>([]);
  const [practiceIndex,setPracticeIndex] = useState(0);
  const [research,setResearch] = useState<Research|null>(null);
  const [selected,setSelected] = useState('');
  const [feedback,setFeedback] = useState<any>(null);
  const [assessmentQuestions,setAssessmentQuestions] = useState<AssessmentQuestion[]>([]);
  const [assessmentAnswers,setAssessmentAnswers] = useState<Record<string,string>>({});
  const [assessmentResult,setAssessmentResult] = useState<any>(null);
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState('');

  const navigate = useNavigate();
  const location = useLocation();
  const step = useMemo(() => ({auth:1,'verify-email':2,'two-factor':2,profile:3,search:4,diagnostic:5,learn:6}[stage]),[stage]);

  useEffect(() => {
    if (stage === 'learn' && !location.pathname.startsWith('/learn')) {
      navigate('/learn/teach', { replace: true });
    }
  }, [location.pathname, navigate, stage]);

  async function run<T>(fn:()=>Promise<T>) {
    setBusy(true);
    setError('');
    try {
      return await fn();
    } catch (e:any) {
      const message = String(e?.message || 'Something went wrong');
      if (/(invalid or expired token|authentication required|two-step verification required)/i.test(message)) {
        clearAuthToken();
        setStage('auth');
        setMode('login');
        setCode('');
        setChallenge('');
        navigate('/', { replace: true });
      }
      setError(message);
      throw e;
    } finally {
      setBusy(false);
    }
  }

  async function submitAuth(e:React.FormEvent){
    e.preventDefault();
    try {
      if(mode==='register'){
        const r:any = await run(()=>apiCall('/api/v1/auth/register',{method:'POST',body:JSON.stringify({full_name:name,email,password})}));
        setDevCode(r.dev_code||''); setStage('verify-email'); return;
      }
      const r:any = await run(()=>apiCall('/api/v1/auth/login',{method:'POST',body:JSON.stringify({email,password})}));
      setChallenge(r.challenge_id); setDevCode(r.dev_code||''); setStage('two-factor');
    } catch {}
  }

  async function verifyEmail(){
    try { await run(()=>apiCall('/api/v1/auth/verify-email',{method:'POST',body:JSON.stringify({email,code})})); setCode(''); setMode('login'); setStage('auth'); } catch {}
  }

  async function verify2fa(){
    try {
      await run(()=>apiCall('/api/v1/auth/verify-2fa',{method:'POST',body:JSON.stringify({challenge_id:challenge,code})}));
      const r:any = await apiCall('/api/v1/auth/complete-login',{method:'POST',body:JSON.stringify({challenge_id:challenge})});
      setAuthToken(r.access_token); setCode(''); setStage('profile');
    } catch {}
  }

  async function saveProfile(){
    try { await run(()=>apiCall('/api/v1/profile',{method:'PATCH',body:JSON.stringify({full_name:name||undefined,learning_goal:goal,education_level:educationLevel,preferred_style:preferredStyle})})); setStage('search'); } catch {}
  }

  async function searchTopics(){
    try { const r:any = await run(()=>apiCall(`/api/v1/topics/search?q=${encodeURIComponent(query)}`)); setTopics(r.topics||[]); } catch {}
  }

  function createLessonSets(topic:string, lessonData: Lesson|null): LessonSet[] {
    const content = lessonData?.output?.content ?? {};
    const curriculumTree = Array.isArray(content.curriculum_tree) ? content.curriculum_tree as Array<{stage?:string;title?:string;goal?:string}> : [];

    if (curriculumTree.length) {
      return curriculumTree.map((step, index) => ({
        id: `lesson-${index}`,
        stage: step.stage || `Lesson ${index + 1}`,
        title: step.title || `${topic} • Lesson ${index + 1}`,
        goal: step.goal || 'Apply the concept in context.',
        explanation: content.detailed_explanation || content.simple_explanation || 'Build the concept one step at a time.',
        learning_goals: Array.isArray(content.learning_objectives) ? content.learning_objectives : ['Understand the concept', 'Apply the idea', 'Check your understanding'],
        milestones: Array.isArray(content.milestones) ? content.milestones : ['Understand the core idea', 'Work through an example', 'Reflect on the result'],
      }));
    }

    return [{
      id: 'lesson-0',
      stage: 'Foundation',
      title: content.title || `${topic} essentials`,
      goal: content.concept || `Build a strong understanding of ${topic}.`,
      explanation: content.detailed_explanation || content.simple_explanation || 'Learn the concept, apply it in examples, and check your understanding.',
      learning_goals: Array.isArray(content.learning_objectives) ? content.learning_objectives : ['Understand the concept', 'Apply the idea', 'Check your understanding'],
      milestones: Array.isArray(content.milestones) ? content.milestones : ['Understand the core idea', 'Work through an example', 'Reflect on the result'],
    }];
  }

  function createPracticeSets(topic:string, lessonData: Lesson|null, practiceData: Practice|null): PracticeSet[] {
    const content = practiceData?.output?.content ?? {};
    const lessonChoices = createLessonSets(topic, lessonData);

    if (lessonChoices.length === 1) {
      return [{
        id: lessonChoices[0].id,
        lessonTitle: lessonChoices[0].title,
        question: content.question || 'Which answer best matches the concept?',
        choices: Array.isArray(content.choices) ? content.choices : [],
        correct_answer: content.correct_answer || '',
        explanation: content.explanation || 'Use the core principle and justify the answer.',
        hint: content.hint || 'Think about the main idea before choosing.',
        skill_tag: content.skill_tag || 'application',
        difficulty: content.difficulty || 'medium',
      }];
    }

    return lessonChoices.map((lessonChoice, index) => ({
      id: `${lessonChoice.id}-practice`,
      lessonTitle: lessonChoice.title,
      question: content.question || `Practice task ${index + 1} for ${lessonChoice.title}?`,
      choices: Array.isArray(content.choices) ? content.choices : ['Apply the concept', 'Skip the example', 'Guess randomly', 'Ignore the feedback'],
      correct_answer: content.correct_answer || (Array.isArray(content.choices) ? content.choices[0] : 'Apply the concept'),
      explanation: content.explanation || `This question checks whether you can apply ${topic} in the context of ${lessonChoice.title}.`,
      hint: content.hint || 'Review the lesson goal before selecting the answer.',
      skill_tag: content.skill_tag || 'application',
      difficulty: content.difficulty || 'medium',
    }));
  }

  async function startTopic(t:string){
    setTopic(t); setAnswers({}); setDiagnostic(null); setSelected(''); setFeedback(null);
    try { const r:any = await run(()=>apiCall(`/api/v1/diagnostic/questions?topic=${encodeURIComponent(t)}`)); setQuestions(r.questions||[]); setStage('diagnostic'); } catch {}
  }

  async function gradeDiagnostic(){
    const payload = questions.map(q => ({ question_id:q.id, answer:answers[q.id]||'' }));
    try {
      const r:any = await run(()=>apiCall('/api/v1/diagnostic/grade',{method:'POST',body:JSON.stringify({topic,answers:payload})}));
      setDiagnostic(r); setLevel(r.level||'beginner');
      const [lessonResult, researchResult] = await Promise.all([
        apiCall<Lesson>('/api/v1/teach',{method:'POST',body:JSON.stringify({topic,level:r.level||'beginner',language:'en'})}),
        apiCall<Research>(`/api/v1/research?q=${encodeURIComponent(topic)}&limit=4`),
      ]);

      const difficulty = r.level === 'advanced' ? 'hard' : r.level === 'intermediate' ? 'medium' : 'easy';
      const generatedLessonSets = createLessonSets(topic, lessonResult);
      const generatedPracticeSets = await Promise.all(
        generatedLessonSets.map(async (_, index) => {
          const current = await apiCall<Practice>('/api/v1/practice',{method:'POST',body:JSON.stringify({topic,difficulty,kind:'mcq'})});
          return {
            id: `${generatedLessonSets[index].id}-practice`,
            lessonTitle: generatedLessonSets[index].title,
            ...(current.output?.content ?? {}),
          } as PracticeSet;
        })
      );

      setLesson(lessonResult); setLessonSets(generatedLessonSets); setLessonIndex(0);
      setPractice(generatedPracticeSets[0] ?? null); setPracticeSets(generatedPracticeSets); setPracticeIndex(0);
      setResearch(researchResult); setStage('learn');
      navigate('/learn/teach', { replace: true });
    } catch {}
  }

  async function checkPractice(){
    const c:any = practiceSets[practiceIndex] || practice?.output?.content; if(!c?.correct_answer||!selected) return;
    if(selected===c.correct_answer){ setFeedback({ok:true,summary:'Correct. You can move to the next challenge.',steps:[c.explanation]}); return; }
    try {
      const r:any = await run(()=>apiCall('/api/v1/mistakes/analyze',{method:'POST',body:JSON.stringify({student_answer:selected,correct_answer:c.correct_answer,context:`${topic} at ${level} level`})}));
      setFeedback({ok:false,...r.output?.content});
    } catch {}
  }

  async function loadNextPractice(){
    if (practiceSets.length > 1) {
      const nextIndex = practiceIndex + 1 < practiceSets.length ? practiceIndex + 1 : 0;
      setPracticeIndex(nextIndex);
      setPractice(practiceSets[nextIndex] ?? null);
      setSelected(''); setFeedback(null); setAssessmentQuestions([]); setAssessmentAnswers({}); setAssessmentResult(null);
      return;
    }

    const difficulty = level === 'advanced' ? 'hard' : level === 'intermediate' ? 'medium' : 'easy';
    try {
      const r:any = await run(()=>apiCall('/api/v1/practice',{method:'POST',body:JSON.stringify({topic,difficulty,kind:'mcq'})}));
      setPractice(r); setPracticeSets([r.output?.content ? { id:'practice-fallback', lessonTitle: lessonSets[0]?.title || topic, ...(r.output.content as any) } : { id:'practice-fallback', lessonTitle: lessonSets[0]?.title || topic }]); setPracticeIndex(0);
      setSelected(''); setFeedback(null); setAssessmentQuestions([]); setAssessmentAnswers({}); setAssessmentResult(null);
    } catch {}
  }

  async function gradeAssessment(){
    if (!assessmentQuestions.length) return;
    const payload = assessmentQuestions.map(q => ({
      question_id:q.id,
      answer:assessmentAnswers[q.id] || '',
      correct:(assessmentAnswers[q.id] || '') === q.correct_answer,
      topic,
    }));
    try {
      const r:any = await run(()=>apiCall('/api/v1/assessment/grade',{method:'POST',body:JSON.stringify(payload)}));
      const progress:any = await apiCall('/api/v1/progress');
      const path:any = await apiCall('/api/v1/learning-path/recommend',{method:'POST',body:JSON.stringify({goal:goal||topic,current_level:level,mastery:progress.mastery,recent_history:progress.recentHistory})});
      setAssessmentResult({...r, mastery:progress.mastery, recommended_path:path});
    } catch {}
  }

  async function askMentor(){
    if(!mentorMessage.trim()) return;
    try {
      const r:any = await run(()=>apiCall('/api/v1/mentor/assist',{method:'POST',body:JSON.stringify({message:mentorMessage,topic:topic||query||undefined,level})}));
      setMentorReply(r);
    } catch {}
  }

  function logout(){ clearAuthToken(); setStage('auth'); setEmail(''); setPassword(''); setChallenge(''); setTopic(''); setAssessmentQuestions([]); setAssessmentAnswers({}); setAssessmentResult(null); navigate('/', { replace: true }); }

  return <main className="min-h-screen bg-slate-950 text-slate-100">
    <div className="mx-auto max-w-6xl px-5 py-8">
      <header className="mb-8 flex items-center justify-between gap-4">
        <div><div className="text-xs font-semibold uppercase tracking-[.28em] text-cyan-300">MentorSLM</div><h1 className="text-2xl font-bold">Adaptive AI Tutor</h1></div>
        {getAuthToken() && <button onClick={logout} className="rounded-xl border border-slate-700 px-4 py-2 text-sm">Sign out</button>}
      </header>

      <div className="mb-8 grid grid-cols-6 gap-2 text-center text-xs text-slate-400">
        {['Account','Verify','Profile','Topic','Diagnostic','Learn'].map((s,i)=><div key={s} className={`rounded-full px-2 py-2 ${step>=i+1?'bg-cyan-400 text-slate-950':'bg-slate-900'}`}>{s}</div>)}
      </div>

      {error && <div className="mb-5 rounded-2xl border border-rose-500/40 bg-rose-500/10 p-4 text-rose-200">{error}</div>}

      {stage==='auth' && <section className="mx-auto max-w-md rounded-3xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="text-2xl font-bold">{mode==='login'?'Sign in':'Create student account'}</h2>
        <p className="mt-2 text-sm text-slate-400">Email verification and two-step verification protect each learner profile.</p>
        <form onSubmit={submitAuth} className="mt-6 space-y-4">
          {mode==='register'&&<input className="w-full rounded-xl bg-slate-800 p-3" placeholder="Full name" value={name} onChange={e=>setName(e.target.value)} required/>}
          <input className="w-full rounded-xl bg-slate-800 p-3" type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required/>
          <input className="w-full rounded-xl bg-slate-800 p-3" type="password" placeholder="Password (8+ characters)" value={password} onChange={e=>setPassword(e.target.value)} required minLength={8}/>
          <button disabled={busy} className="w-full rounded-xl bg-cyan-400 p-3 font-semibold text-slate-950">{busy?'Working…':mode==='login'?'Continue':'Create account'}</button>
        </form>
        <button onClick={()=>setMode(mode==='login'?'register':'login')} className="mt-4 text-sm text-cyan-300">{mode==='login'?'Need an account? Sign up':'Already registered? Sign in'}</button>
      </section>}

      {stage==='verify-email' && <VerifyCard title="Verify your email" description="Enter the 6-digit code sent to your email." code={code} setCode={setCode} devCode={devCode} action={verifyEmail} busy={busy}/>} 
      {stage==='two-factor' && <VerifyCard title="Two-step verification" description="Enter your second-factor code to finish signing in." code={code} setCode={setCode} devCode={devCode} action={verify2fa} busy={busy}/>} 

      {stage==='profile' && <section className="mx-auto max-w-xl rounded-3xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="text-2xl font-bold">Build your learner profile</h2><p className="mt-2 text-slate-400">This becomes the starting context for your Student Model.</p>
        <div className="mt-6 space-y-4"><input className="w-full rounded-xl bg-slate-800 p-3" placeholder="Full name" value={name} onChange={e=>setName(e.target.value)}/><input className="w-full rounded-xl bg-slate-800 p-3" placeholder="Education level (e.g. Undergraduate)" value={educationLevel} onChange={e=>setEducationLevel(e.target.value)}/><textarea className="w-full rounded-xl bg-slate-800 p-3" placeholder="What do you want to learn or achieve?" value={goal} onChange={e=>setGoal(e.target.value)}/><select className="w-full rounded-xl bg-slate-800 p-3" value={preferredStyle} onChange={e=>setPreferredStyle(e.target.value)}><option>Step-by-step explanations</option><option>Visual examples and analogies</option><option>Project-based learning</option><option>Challenge me quickly</option></select><button onClick={saveProfile} className="w-full rounded-xl bg-cyan-400 p-3 font-semibold text-slate-950">Start learning</button></div>
      </section>}

      {stage==='search' && <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="text-2xl font-bold">What do you want to learn?</h2><p className="mt-2 text-slate-400">Search a topic. MentorSLM will check your current knowledge before teaching.</p>
        <div className="mt-5 flex gap-3"><input className="min-w-0 flex-1 rounded-xl bg-slate-800 p-3" placeholder="Python, mathematics, data science…" value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>{if(e.key==='Enter') void searchTopics();}}/><button onClick={searchTopics} className="rounded-xl bg-cyan-400 px-5 font-semibold text-slate-950">Search</button></div>
        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{topics.map(t=><button key={t} onClick={()=>startTopic(t)} className="rounded-2xl border border-slate-700 bg-slate-800 p-4 text-left hover:border-cyan-400"><div className="font-semibold">{t}</div><div className="mt-1 text-xs text-slate-400">Start knowledge check →</div></button>)}</div>
      </section>}

      {stage==='diagnostic' && <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6"><div className="mb-6"><div className="text-sm text-cyan-300">Knowledge Assessment</div><h2 className="text-2xl font-bold">{topic}</h2><p className="text-slate-400">This diagnostic sets your starting level; it is not a final exam.</p></div><div className="space-y-5">{questions.map((q,i)=><div key={q.id} className="rounded-2xl bg-slate-800 p-4"><div className="font-medium">{i+1}. {q.question}</div><div className="mt-3 grid gap-2 sm:grid-cols-2">{q.options.map(o=><button key={o} onClick={()=>setAnswers(a=>({...a,[q.id]:o}))} className={`rounded-xl border p-3 text-left ${answers[q.id]===o?'border-cyan-400 bg-cyan-400/10':'border-slate-700'}`}>{o}</button>)}</div></div>)}</div><button disabled={Object.keys(answers).length!==questions.length||busy} onClick={gradeDiagnostic} className="mt-6 w-full rounded-xl bg-cyan-400 p-3 font-semibold text-slate-950 disabled:opacity-40">Build my learning path</button></section>}

      {stage==='learn' && <LearningPages topic={topic} level={level} diagnostic={diagnostic} lesson={lesson} lessonSets={lessonSets} lessonIndex={lessonIndex} setLessonIndex={setLessonIndex} practice={practice} practiceSets={practiceSets} practiceIndex={practiceIndex} setPracticeIndex={setPracticeIndex} research={research} selected={selected} setSelected={setSelected} feedback={feedback} setFeedback={setFeedback} busy={busy} onCheckPractice={checkPractice} onNextPractice={loadNextPractice} assessmentQuestions={assessmentQuestions} setAssessmentQuestions={setAssessmentQuestions} assessmentAnswers={assessmentAnswers} setAssessmentAnswers={setAssessmentAnswers} assessmentResult={assessmentResult} setAssessmentResult={setAssessmentResult} onGradeAssessment={gradeAssessment} />}
      {getAuthToken() && <><button aria-label="Open Mentor assistant" onClick={()=>setMentorOpen(v=>!v)} className="fixed bottom-6 right-6 z-40 rounded-full bg-cyan-400 px-5 py-4 font-bold text-slate-950 shadow-2xl">Mentor AI</button>{mentorOpen&&<div className="fixed bottom-24 right-6 z-40 w-[min(380px,calc(100vw-3rem))] rounded-3xl border border-slate-700 bg-slate-900 p-5 shadow-2xl"><div className="font-bold">Learning assistant</div><p className="mt-1 text-xs text-slate-400">Ask for a roadmap, concept help, or your next learning step.</p>{mentorReply&&<div className="mt-4 rounded-2xl bg-slate-800 p-3 text-sm"><p>{mentorReply.answer}</p><div className="mt-3 flex flex-wrap gap-2">{mentorReply.suggested_actions?.map((x:string)=><span key={x} className="rounded-full bg-cyan-400/10 px-2 py-1 text-xs text-cyan-200">{x}</span>)}</div></div>}<textarea value={mentorMessage} onChange={e=>setMentorMessage(e.target.value)} className="mt-4 w-full rounded-xl bg-slate-800 p-3 text-sm" placeholder="I want to become a programmer. What should I learn next?"/><button onClick={askMentor} disabled={busy||!mentorMessage.trim()} className="mt-3 w-full rounded-xl bg-cyan-400 p-3 font-semibold text-slate-950 disabled:opacity-40">Ask Mentor</button></div>}</>}
    </div>
  </main>
}

function LearningPages({
  topic, level, diagnostic, lesson, lessonSets, lessonIndex, setLessonIndex, practice, practiceSets, practiceIndex, setPracticeIndex, research, selected, setSelected, feedback, setFeedback, busy,
  onCheckPractice, onNextPractice, assessmentQuestions, setAssessmentQuestions, assessmentAnswers, setAssessmentAnswers,
  assessmentResult, setAssessmentResult, onGradeAssessment,
}:{
  topic:string; level:string; diagnostic:any; lesson:Lesson|null; lessonSets:LessonSet[]; lessonIndex:number; setLessonIndex:Dispatch<SetStateAction<number>>; practice:Practice|null; practiceSets:PracticeSet[]; practiceIndex:number; setPracticeIndex:Dispatch<SetStateAction<number>>; research:Research|null; selected:string;
  setSelected:Dispatch<SetStateAction<string>>; feedback:any; setFeedback:Dispatch<SetStateAction<any>>; busy:boolean; onCheckPractice:()=>void; onNextPractice:()=>void;
  assessmentQuestions:AssessmentQuestion[]; setAssessmentQuestions:Dispatch<SetStateAction<AssessmentQuestion[]>>; assessmentAnswers:Record<string,string>;
  setAssessmentAnswers:Dispatch<SetStateAction<Record<string,string>>>; assessmentResult:any; setAssessmentResult:Dispatch<SetStateAction<any>>; onGradeAssessment:()=>void;
}) {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (assessmentQuestions.length === 0 && topic) {
      const seedQuestions: AssessmentQuestion[] = [
        { id:'assessment-1', question:`Which answer best matches the concept of ${topic}?`, options:['Apply the core concept consistently','Skip the lesson','Guess randomly','Ignore the examples'], correct_answer:'Apply the core concept consistently' },
        { id:'assessment-2', question:`What is the best next step when learning ${topic}?`, options:['Review the key idea and practice with examples','Move on without checking understanding','Avoid feedback','Skip exercises'], correct_answer:'Review the key idea and practice with examples' },
        { id:'assessment-3', question:`Which statement is most accurate for ${topic}?`, options:['Strong understanding comes from applying the concept in context','The answer is always random','Examples are unnecessary','Mistakes should be ignored'], correct_answer:'Strong understanding comes from applying the concept in context' },
      ];
      setAssessmentQuestions(seedQuestions);
      setAssessmentAnswers({});
      setAssessmentResult(null);
    }
  }, [assessmentQuestions.length, setAssessmentAnswers, setAssessmentQuestions, setAssessmentResult, topic]);

  return <div className="space-y-6">
    <section className="grid gap-4 md:grid-cols-4"><Stat label="Topic" value={topic}/><Stat label="Starting level" value={level}/><Stat label="Diagnostic" value={`${diagnostic?.score ?? 0}%`}/><Stat label="Weak areas" value={(diagnostic?.weaknesses||[]).join(', ')||'None detected'}/></section>

    <div className="rounded-3xl border border-slate-800 bg-slate-900 p-5">
      <div className="mb-5 flex flex-wrap gap-2">
        {[
          { label:'Teaching Engine', path:'/learn/teach' },
          { label:'Practice Engine', path:'/learn/practice' },
          { label:'Research Engine', path:'/learn/research' },
          { label:'Assessment Engine', path:'/learn/assessment' },
        ].map(({label, path}) => (
          <button key={path} onClick={() => navigate(path)} className={`rounded-full px-4 py-2 text-sm font-medium ${location.pathname === path ? 'bg-cyan-400 text-slate-950' : 'border border-slate-700 bg-slate-800 text-slate-200'}`}>
            {label}
          </button>
        ))}
      </div>

      <Routes>
        <Route path="/learn/teach" element={<TeachingPage topic={topic} lesson={lesson} lessonSets={lessonSets} lessonIndex={lessonIndex} setLessonIndex={setLessonIndex} />} />
        <Route path="/learn/practice" element={<PracticePage practice={practice} practiceSets={practiceSets} practiceIndex={practiceIndex} setPracticeIndex={setPracticeIndex} selected={selected} setSelected={setSelected} feedback={feedback} setFeedback={setFeedback} busy={busy} onCheckPractice={onCheckPractice} onNextPractice={onNextPractice} onGoToAssessment={() => navigate('/learn/assessment')} />} />
        <Route path="/learn/research" element={<ResearchPage research={research} />} />
        <Route path="/learn/assessment" element={<AssessmentPage assessmentQuestions={assessmentQuestions} assessmentAnswers={assessmentAnswers} setAssessmentAnswers={setAssessmentAnswers} assessmentResult={assessmentResult} onGradeAssessment={onGradeAssessment} />} />
        <Route path="/learn" element={<Navigate to="/learn/teach" replace />} />
      </Routes>
    </div>
  </div>
}

function TeachingPage({ topic, lesson, lessonSets, lessonIndex, setLessonIndex }:{ topic:string; lesson:Lesson|null; lessonSets:LessonSet[]; lessonIndex:number; setLessonIndex:Dispatch<SetStateAction<number>>; }) {
  const currentLesson = lessonSets[lessonIndex] || lessonSets[0] || { id:'lesson-0', stage:'Foundation', title:`${topic} lesson`, goal:'Build the concept strongly', explanation: lesson?.output?.content?.detailed_explanation || lesson?.output?.content?.simple_explanation || 'Learn the concept step by step.', learning_goals: ['Understand the key concept','Apply the idea to examples','Check your understanding'], milestones: ['Understand the core idea','Work through an example','Reflect on the result'] };

  return <div className="space-y-6">
    <div className="flex items-center justify-between gap-3"><div><div className="text-sm text-cyan-300">Teacher SLM · Teaching Engine</div><h2 className="mt-1 text-2xl font-bold">{currentLesson.title}</h2></div><div className="flex gap-2"><button onClick={()=>setLessonIndex(i => Math.max(0, i - 1))} disabled={lessonIndex===0} className="rounded-xl border border-slate-700 bg-slate-800 px-3 py-2 text-sm disabled:opacity-40">Previous</button><button onClick={()=>setLessonIndex(i => Math.min(lessonSets.length - 1 || 0, i + 1))} disabled={lessonSets.length <= 1 || lessonIndex >= lessonSets.length - 1} className="rounded-xl bg-cyan-400 px-3 py-2 text-sm font-semibold text-slate-950 disabled:opacity-40">Next lesson</button></div></div>

    <div className="grid gap-6 lg:grid-cols-[1.35fr_.65fr]">
      <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
        <div className="text-xs uppercase tracking-[.2em] text-cyan-300">{currentLesson.stage}</div>
        <p className="mt-4 text-lg">{currentLesson.goal}</p>
        <p className="mt-4 text-slate-300">{currentLesson.explanation}</p>
        <div className="mt-5 rounded-2xl bg-slate-800 p-4"><div className="text-xs uppercase tracking-wider text-slate-400">Milestones</div><ul className="mt-2 list-disc space-y-1 pl-5 text-sm">{(currentLesson.milestones || [lesson?.output?.content?.practice_question || 'Build confidence with examples']).map((m:string)=><li key={m}>{m}</li>)}</ul></div>
      </div>
      <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6"><div className="text-sm text-cyan-300">Learning goals</div><div className="mt-4 space-y-3">{(currentLesson.learning_goals || ['Understand the key concept','Apply the idea to examples','Check your understanding']).map((g:string)=><div key={g} className="rounded-2xl bg-slate-800 p-3 text-sm">{g}</div>)}</div></div>
    </div>
  </div>
}

function PracticePage({ practice, practiceSets, practiceIndex, setPracticeIndex, selected, setSelected, feedback, setFeedback, busy, onCheckPractice, onNextPractice, onGoToAssessment }:{ practice:Practice|null; practiceSets:PracticeSet[]; practiceIndex:number; setPracticeIndex:Dispatch<SetStateAction<number>>; selected:string; setSelected:Dispatch<SetStateAction<string>>; feedback:any; setFeedback:Dispatch<SetStateAction<any>>; busy:boolean; onCheckPractice:()=>void; onNextPractice:()=>void; onGoToAssessment:()=>void; }) {
  const currentPractice = practiceSets[practiceIndex] || { id:'fallback-practice', lessonTitle:'Practice', question: practice?.output?.content?.question || 'Which answer best matches the concept?', choices: practice?.output?.content?.choices || [], correct_answer: practice?.output?.content?.correct_answer || '', explanation: practice?.output?.content?.explanation || 'Use the concept to justify the answer.' };

  return <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6"><div className="flex items-start justify-between gap-3"><div><div className="text-sm text-cyan-300">Practice Engine + Mistake Analyzer</div><h3 className="mt-1 text-xl font-bold">Try it yourself</h3></div>{practiceSets.length > 1 && <div className="flex gap-2"><button onClick={()=>setPracticeIndex(i => Math.max(0, i - 1))} disabled={practiceIndex===0} className="rounded-xl border border-slate-700 bg-slate-800 px-3 py-2 text-sm disabled:opacity-40">Previous</button><button onClick={()=>setPracticeIndex(i => Math.min(practiceSets.length - 1, i + 1))} disabled={practiceIndex >= practiceSets.length - 1} className="rounded-xl bg-cyan-400 px-3 py-2 text-sm font-semibold text-slate-950 disabled:opacity-40">Next set</button></div>}</div><div className="mt-3 rounded-2xl border border-slate-700 bg-slate-800 px-3 py-2 text-xs uppercase tracking-[.2em] text-cyan-300">{currentPractice.lessonTitle || 'Practice set'}</div><p className="mt-3 text-lg">{currentPractice.question}</p><div className="mt-4 grid gap-3 sm:grid-cols-2">{currentPractice.choices?.map(o=><button key={o} onClick={()=>{setSelected(o); setFeedback(null)}} className={`rounded-xl border p-3 text-left ${selected===o?'border-cyan-400 bg-cyan-400/10':'border-slate-700 bg-slate-800'}`}>{o}</button>)}</div><div className="mt-4 flex flex-wrap gap-3"><button onClick={onCheckPractice} disabled={!selected} className="rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-40">Check my reasoning</button><button onClick={onNextPractice} disabled={busy} className="rounded-xl border border-slate-700 bg-slate-800 px-5 py-3 font-semibold text-slate-100 disabled:opacity-40">Next problem</button><button onClick={onGoToAssessment} className="rounded-xl border border-cyan-400/60 bg-cyan-400/10 px-5 py-3 font-semibold text-cyan-200">Go to assessment engine</button></div>{feedback&&<div className={`mt-5 rounded-2xl p-4 ${feedback.ok?'bg-emerald-500/10':'bg-amber-500/10'}`}><div className="font-semibold">{feedback.ok?'Well done':'Let’s fix the mistake'}</div><p className="mt-2 text-sm">{feedback.summary||feedback.root_cause}</p>{feedback.improvement_steps&&<ul className="mt-3 list-disc space-y-1 pl-5 text-sm">{feedback.improvement_steps.map((x:string)=><li key={x}>{x}</li>)}</ul>}</div>}</section>
}

function ResearchPage({ research }:{ research:Research|null; }) {
  return <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6"><div className="text-sm text-cyan-300">Research Engine</div><h3 className="mt-1 text-xl font-bold">Recommended sources</h3><div className="mt-4 space-y-3">{research?.output?.content?.sources?.map(s=><a key={s.url} href={s.url} target="_blank" rel="noreferrer" className="block rounded-2xl bg-slate-800 p-3"><div className="font-medium">{s.title}</div><div className="mt-1 text-xs text-slate-400">{s.publisher}</div></a>)}</div></section>
}

function AssessmentPage({ assessmentQuestions, assessmentAnswers, setAssessmentAnswers, assessmentResult, onGradeAssessment }:{ assessmentQuestions:AssessmentQuestion[]; assessmentAnswers:Record<string,string>; setAssessmentAnswers:Dispatch<SetStateAction<Record<string,string>>>; assessmentResult:any; onGradeAssessment:()=>void; }) {
  const navigate = useNavigate();

  return <section className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
    <div className="flex items-center justify-between gap-3">
      <div><div className="text-sm text-cyan-300">Assessment Engine</div><h3 className="mt-1 text-xl font-bold">Mini assessment</h3></div>
      <button onClick={() => navigate('/learn/practice')} className="rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 text-sm">Back to practice</button>
    </div>
    <div className="mt-5 space-y-5">{assessmentQuestions.map((q,i)=><div key={q.id} className="rounded-2xl bg-slate-800 p-4"><div className="font-medium">{i+1}. {q.question}</div><div className="mt-3 grid gap-2 sm:grid-cols-2">{q.options.map(o=><button key={o} onClick={()=>setAssessmentAnswers(current => ({...current,[q.id]:o}))} className={`rounded-xl border p-3 text-left ${assessmentAnswers[q.id]===o?'border-cyan-400 bg-cyan-400/10':'border-slate-700 bg-slate-800'}`}>{o}</button>)}</div></div>)}</div>
    <button onClick={onGradeAssessment} disabled={assessmentQuestions.length===0 || Object.keys(assessmentAnswers).length !== assessmentQuestions.length} className="mt-6 rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-40">Submit assessment</button>
    {assessmentResult && <div className="mt-5 rounded-2xl border border-cyan-500/30 bg-cyan-500/10 p-4"><div className="font-semibold">Assessment result</div><p className="mt-2 text-sm">Score: {assessmentResult.score * 100}% · {assessmentResult.report}</p><p className="mt-2 text-sm text-slate-300">{assessmentResult.next_step}</p>{assessmentResult.mastery!==undefined&&<p className="mt-2 text-sm text-cyan-200">Recorded mastery: {Math.round(assessmentResult.mastery*100)}%</p>}{assessmentResult.recommended_path&&<p className="mt-2 text-sm text-slate-300">Adaptive path: {assessmentResult.recommended_path.recommendation || assessmentResult.recommended_path.next_step || 'Continue with the recommended learning path.'}</p>}</div>}
  </section>
}

function VerifyCard({title,description,code,setCode,devCode,action,busy}:{title:string;description:string;code:string;setCode:(s:string)=>void;devCode:string;action:()=>void;busy:boolean}){
  return <section className="mx-auto max-w-md rounded-3xl border border-slate-800 bg-slate-900 p-6"><h2 className="text-2xl font-bold">{title}</h2><p className="mt-2 text-sm text-slate-400">{description}</p>{devCode&&<div className="mt-4 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-200">Demo code: <strong>{devCode}</strong> · disable DEV_OTP_MODE in production.</div>}<input className="mt-5 w-full rounded-xl bg-slate-800 p-3 text-center text-2xl tracking-[.4em]" value={code} onChange={e=>setCode(e.target.value.replace(/\D/g,'').slice(0,6))} placeholder="000000"/><button onClick={action} disabled={code.length!==6||busy} className="mt-4 w-full rounded-xl bg-cyan-400 p-3 font-semibold text-slate-950 disabled:opacity-40">Verify</button></section>
}

function Stat({label,value}:{label:string;value:string}){ return <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4"><div className="text-xs uppercase tracking-wider text-slate-400">{label}</div><div className="mt-2 font-semibold">{value}</div></div> }
