from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD_HTML


DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Healthcare DMS</title>
<style>
:root {
    --primary: #0f3460; --primary-light: #1a4a8a; --primary-bg: #e8eef6;
    --green: #059669; --green-bg: #d1fae5; --amber: #d97706; --amber-bg: #fef3c7;
    --red: #dc2626; --red-bg: #fee2e2; --blue: #2563eb; --blue-bg: #dbeafe;
    --gray-50: #f8fafc; --gray-100: #f1f5f9; --gray-200: #e2e8f0; --gray-400: #94a3b8;
    --gray-500: #64748b; --gray-700: #334155; --gray-900: #0f172a;
    --radius: 10px; --shadow: 0 2px 12px rgba(0,0,0,0.06);
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',system-ui,-apple-system,sans-serif; background:var(--gray-100); color:var(--gray-900); }

/* Header */
.header { background:linear-gradient(135deg,var(--primary),#16213e); color:#fff; padding:16px 28px; display:flex; justify-content:space-between; align-items:center; position:sticky; top:0; z-index:100; }
.header h1 { font-size:1.25rem; font-weight:600; }
.header .right { display:flex; align-items:center; gap:14px; }
.header .user-info { font-size:.85rem; opacity:.85; }
.hbtn { background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.25); color:#fff; padding:5px 14px; border-radius:6px; cursor:pointer; font-size:.82rem; }
.hbtn:hover { background:rgba(255,255,255,.22); }

/* Nav tabs */
.nav { background:#fff; border-bottom:1px solid var(--gray-200); padding:0 28px; display:flex; gap:0; }
.nav-tab { padding:12px 20px; font-size:.9rem; cursor:pointer; border-bottom:3px solid transparent; color:var(--gray-500); font-weight:500; transition:all .15s; user-select:none; }
.nav-tab:hover { color:var(--primary); background:var(--gray-50); }
.nav-tab.active { color:var(--primary); border-bottom-color:var(--primary); font-weight:600; }

/* Layout */
.container { max-width:1240px; margin:0 auto; padding:20px 24px; }
.page { display:none; }
.page.active { display:block; }

/* Cards */
.stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:14px; margin-bottom:24px; }
.card { background:#fff; border-radius:var(--radius); padding:20px; box-shadow:var(--shadow); }
.card .lbl { font-size:.78rem; color:var(--gray-500); text-transform:uppercase; letter-spacing:.4px; margin-bottom:4px; }
.card .val { font-size:1.8rem; font-weight:700; color:var(--primary); }
.card.green .val { color:var(--green); }
.card.amber .val { color:var(--amber); }
.card.red .val { color:var(--red); }

/* Sections & tables */
.section { background:#fff; border-radius:var(--radius); padding:20px 24px; margin-bottom:18px; box-shadow:var(--shadow); }
.section-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; flex-wrap:wrap; gap:10px; }
.section-head h3 { font-size:1.05rem; color:var(--primary); }
.search-box { padding:7px 14px; border:1px solid var(--gray-200); border-radius:8px; font-size:.88rem; width:260px; outline:none; }
.search-box:focus { border-color:var(--primary); box-shadow:0 0 0 2px var(--primary-bg); }
table { width:100%; border-collapse:collapse; }
th { text-align:left; padding:9px 12px; background:var(--gray-50); color:var(--gray-500); font-size:.76rem; text-transform:uppercase; letter-spacing:.4px; border-bottom:2px solid var(--gray-200); }
td { padding:9px 12px; border-bottom:1px solid var(--gray-100); font-size:.88rem; }
tr:hover td { background:var(--gray-50); }
.clickable { color:var(--blue); cursor:pointer; font-weight:500; }
.clickable:hover { text-decoration:underline; }
.badge { display:inline-block; padding:2px 10px; border-radius:10px; font-size:.76rem; font-weight:600; }
.badge.scheduled { background:var(--blue-bg); color:var(--blue); }
.badge.completed { background:var(--green-bg); color:var(--green); }
.badge.cancelled { background:var(--red-bg); color:var(--red); }
.empty { text-align:center; padding:30px; color:var(--gray-400); }

/* Bar charts */
.bars { display:flex; flex-direction:column; gap:8px; }
.bar-row { display:flex; align-items:center; gap:10px; }
.bar-lbl { min-width:100px; font-size:.85rem; text-align:right; color:var(--gray-700); }
.bar-track { flex:1; background:var(--gray-200); border-radius:6px; height:26px; overflow:hidden; }
.bar-fill { height:100%; border-radius:6px; display:flex; align-items:center; padding-left:10px; color:#fff; font-size:.78rem; font-weight:600; min-width:28px; transition:width .5s ease; }
.grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-bottom:18px; }

/* Detail panel */
.detail-panel { background:#fff; border-radius:var(--radius); padding:28px; box-shadow:var(--shadow); }
.detail-panel h2 { color:var(--primary); margin-bottom:18px; font-size:1.3rem; }
.detail-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px 24px; margin-bottom:20px; }
.detail-field .dfk { font-size:.76rem; color:var(--gray-500); text-transform:uppercase; letter-spacing:.3px; }
.detail-field .dfv { font-size:1rem; font-weight:500; margin-top:2px; }
.back-btn { display:inline-flex; align-items:center; gap:6px; color:var(--primary); cursor:pointer; font-size:.9rem; font-weight:500; margin-bottom:16px; user-select:none; }
.back-btn:hover { text-decoration:underline; }

/* Login */
.login-wrap { display:flex; justify-content:center; align-items:center; min-height:90vh; }
.login-box { background:#fff; padding:36px; border-radius:12px; box-shadow:0 4px 24px rgba(0,0,0,.08); width:340px; }
.login-box h2 { margin-bottom:20px; text-align:center; color:var(--primary); font-size:1.3rem; }
.login-box input { width:100%; padding:10px 14px; margin-bottom:12px; border:1px solid var(--gray-200); border-radius:8px; font-size:.92rem; }
.login-box button { width:100%; padding:10px; background:var(--primary); color:#fff; border:none; border-radius:8px; font-size:.95rem; cursor:pointer; font-weight:500; }
.login-box button:hover { background:var(--primary-light); }
.login-box .err { color:var(--red); font-size:.83rem; margin-bottom:8px; text-align:center; }

/* Pagination */
.pagination { display:flex; justify-content:center; align-items:center; gap:8px; margin-top:14px; padding-top:10px; }
.pg-btn { padding:6px 12px; border:1px solid var(--gray-200); border-radius:6px; font-size:.84rem; cursor:pointer; background:#fff; }
.pg-btn:hover { background:var(--gray-50); }
.pg-btn.active { background:var(--primary); color:#fff; border-color:var(--primary); }
.pg-btn:disabled { opacity:.4; cursor:default; }
.pg-info { font-size:.84rem; color:var(--gray-500); }

@media(max-width:768px) {
    .grid-2 { grid-template-columns:1fr; }
    .detail-grid { grid-template-columns:1fr; }
    .search-box { width:100%!important; }
    .nav { overflow-x:auto; }
}
</style>
</head>
<body>

<!-- LOGIN -->
<div id="login-screen">
<div class="login-wrap"><div class="login-box">
    <h2>&#9764; Healthcare DMS</h2>
    <div id="login-error" class="err" style="display:none"></div>
    <input id="username" placeholder="Username" value="admin">
    <input id="password" type="password" placeholder="Password" value="admin123">
    <button onclick="doLogin()">Sign In</button>
    <p style="margin-top:14px;font-size:.8rem;color:var(--gray-500);text-align:center">Demo: admin / admin123</p>
</div></div>
</div>

<!-- APP SHELL -->
<div id="app" style="display:none">
<div class="header">
    <h1>&#9764; Healthcare DMS</h1>
    <div class="right">
        <span class="user-info" id="user-label"></span>
        <button class="hbtn" onclick="logout()">Logout</button>
    </div>
</div>
<div class="nav" id="nav">
    <div class="nav-tab active" data-page="overview">Overview</div>
    <div class="nav-tab" data-page="patients">Patients</div>
    <div class="nav-tab" data-page="doctors">Doctors</div>
    <div class="nav-tab" data-page="appointments">Appointments</div>
</div>
<div class="container">

<!-- OVERVIEW -->
<div id="pg-overview" class="page active">
    <div class="stats" id="stats-cards"><div class="empty">Loading...</div></div>
    <div class="grid-2">
        <div class="section"><h3 style="margin-bottom:12px">Patients by Department</h3><div id="dept-chart" class="bars"></div></div>
        <div class="section"><h3 style="margin-bottom:12px">Appointment Status</h3><div id="status-chart" class="bars"></div></div>
    </div>
    <div class="section">
        <div class="section-head"><h3>Recent Patients</h3></div>
        <table><thead><tr><th>Name</th><th>Age</th><th>Gender</th><th>Blood</th><th>Contact</th></tr></thead>
        <tbody id="recent-patients"></tbody></table>
    </div>
</div>

<!-- PATIENTS -->
<div id="pg-patients" class="page">
    <div id="patients-list-view">
        <div class="section">
            <div class="section-head">
                <h3 id="patients-count-label">All Patients</h3>
                <input class="search-box" id="patient-search" placeholder="Search by name, contact, address..." oninput="debouncedSearchPatients()">
            </div>
            <table><thead><tr><th>ID</th><th>Name</th><th>Age</th><th>Gender</th><th>Contact</th><th>Blood</th><th>Address</th></tr></thead>
            <tbody id="patients-tbody"></tbody></table>
            <div id="patients-pagination" class="pagination"></div>
        </div>
    </div>
    <div id="patients-detail-view" style="display:none">
        <div class="detail-panel">
            <div class="back-btn" onclick="showPatientsList()">&#8592; Back to Patients</div>
            <h2 id="pd-name"></h2>
            <div class="detail-grid" id="pd-fields"></div>
            <h3 style="margin:18px 0 12px;color:var(--primary)">Medical Records</h3>
            <table><thead><tr><th>Date</th><th>Doctor</th><th>Diagnosis</th><th>Prescription</th><th>Notes</th></tr></thead>
            <tbody id="pd-records"></tbody></table>
            <h3 style="margin:18px 0 12px;color:var(--primary)">Appointments</h3>
            <table><thead><tr><th>Date &amp; Time</th><th>Doctor</th><th>Reason</th><th>Status</th></tr></thead>
            <tbody id="pd-appointments"></tbody></table>
        </div>
    </div>
</div>

<!-- DOCTORS -->
<div id="pg-doctors" class="page">
    <div id="doctors-list-view">
        <div class="section">
            <div class="section-head">
                <h3 id="doctors-count-label">All Doctors</h3>
                <div style="display:flex;gap:10px;flex-wrap:wrap">
                    <input class="search-box" id="doctor-search" placeholder="Search name, specialization..." oninput="debouncedSearchDoctors()" style="width:240px">
                    <select class="search-box" id="dept-filter" onchange="renderDoctors()" style="width:180px"><option value="">All Departments</option></select>
                </div>
            </div>
            <table><thead><tr><th>ID</th><th>Name</th><th>Specialization</th><th>Department</th><th>Contact</th></tr></thead>
            <tbody id="doctors-tbody"></tbody></table>
        </div>
    </div>
    <div id="doctors-detail-view" style="display:none">
        <div class="detail-panel">
            <div class="back-btn" onclick="showDoctorsList()">&#8592; Back to Doctors</div>
            <h2 id="dd-name"></h2>
            <div class="detail-grid" id="dd-fields"></div>
            <h3 style="margin:18px 0 12px;color:var(--primary)">Appointments</h3>
            <table><thead><tr><th>Date &amp; Time</th><th>Patient</th><th>Reason</th><th>Status</th></tr></thead>
            <tbody id="dd-appointments"></tbody></table>
        </div>
    </div>
</div>

<!-- APPOINTMENTS -->
<div id="pg-appointments" class="page">
    <div class="section">
        <div class="section-head">
            <h3 id="appts-count-label">All Appointments</h3>
            <div style="display:flex;gap:10px;flex-wrap:wrap">
                <input class="search-box" id="appt-search" placeholder="Search patient, doctor, reason..." oninput="debouncedFilterAppts()" style="width:240px">
                <select class="search-box" id="appt-status-filter" onchange="filterAppointments()" style="width:160px">
                    <option value="">All Statuses</option>
                    <option value="scheduled">Scheduled</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                </select>
            </div>
        </div>
        <table><thead><tr><th>ID</th><th>Patient</th><th>Doctor</th><th>Date &amp; Time</th><th>Reason</th><th>Status</th></tr></thead>
        <tbody id="appts-tbody"></tbody></table>
        <div id="appts-pagination" class="pagination"></div>
    </div>
</div>

</div>
</div>

<script>
/* ===== State ===== */
const API='';
let TOKEN='',ROLE='';
let allPatients=[],allDoctors=[],allAppointments=[];
const PAGE_SIZE=15;
let patientPage=1,apptPage=1;

/* ===== XSS-safe escape ===== */
const _e=document.createElement('div');
function esc(s){if(s==null)return'';_e.textContent=String(s);return _e.innerHTML;}

/* ===== Debounce helper ===== */
function debounce(fn,ms){let t;return(...a)=>{clearTimeout(t);t=setTimeout(()=>fn(...a),ms);};}
const debouncedSearchPatients=debounce(()=>{patientPage=1;renderPatients();},250);
const debouncedSearchDoctors=debounce(renderDoctors,250);
const debouncedFilterAppts=debounce(()=>{apptPage=1;renderAppointments();},250);

/* ===== Auth ===== */
async function doLogin(){
    const u=document.getElementById('username').value,p=document.getElementById('password').value;
    const err=document.getElementById('login-error');err.style.display='none';
    try{
        const r=await fetch(API+'/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
        if(!r.ok){err.textContent='Invalid credentials';err.style.display='block';return;}
        TOKEN=(await r.json()).access_token;
        document.getElementById('login-screen').style.display='none';
        document.getElementById('app').style.display='block';
        initApp();
    }catch(e){err.textContent='Server unreachable';err.style.display='block';}
}
function logout(){TOKEN='';document.getElementById('app').style.display='none';document.getElementById('login-screen').style.display='block';}
function hdr(){return{'Authorization':'Bearer '+TOKEN,'Content-Type':'application/json'};}
async function api(path){const r=await fetch(API+path,{headers:hdr()});if(!r.ok)throw new Error(r.status);return r.json();}
document.getElementById('password').addEventListener('keydown',e=>{if(e.key==='Enter')doLogin();});

/* ===== Nav ===== */
document.querySelectorAll('.nav-tab').forEach(tab=>{
    tab.addEventListener('click',()=>{
        document.querySelectorAll('.nav-tab').forEach(t=>t.classList.remove('active'));
        document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
        tab.classList.add('active');
        const pg=document.getElementById('pg-'+tab.dataset.page);
        pg.classList.add('active');
        // Render on tab switch
        if(tab.dataset.page==='patients'&&document.getElementById('patients-list-view').style.display!=='none')renderPatients();
        if(tab.dataset.page==='doctors'&&document.getElementById('doctors-list-view').style.display!=='none')renderDoctors();
        if(tab.dataset.page==='appointments')renderAppointments();
    });
});
function activateTab(name){
    document.querySelectorAll('.nav-tab').forEach(t=>t.classList.remove('active'));
    document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
    const tab=document.querySelector('.nav-tab[data-page="'+name+'"]');
    if(tab)tab.classList.add('active');
    document.getElementById('pg-'+name).classList.add('active');
}

/* ===== Init ===== */
async function initApp(){
    try{const me=await api('/auth/me');ROLE=me.role;document.getElementById('user-label').textContent=me.full_name+' ('+me.role+')';}catch(e){}
    await Promise.all([loadPatients(),loadDoctors(),loadAppointments()]);
    loadOverview();
}
async function loadPatients(){try{allPatients=await api('/patients/');}catch(e){allPatients=[];}}
async function loadDoctors(){try{allDoctors=await api('/doctors/');}catch(e){allDoctors=[];} populateDeptFilter();}
async function loadAppointments(){try{allAppointments=await api('/appointments/');}catch(e){allAppointments=[];}}

function doctorName(id){const d=allDoctors.find(x=>x.id===id);return d?d.name:'Doctor #'+id;}
function patientName(id){const p=allPatients.find(x=>x.id===id);return p?p.name:'Patient #'+id;}
function fmtDate(s){if(!s)return'-';const d=new Date(s);return d.toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'})+' '+d.toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit'});}
function detailFields(obj){return Object.entries(obj).map(([k,v])=>'<div class="detail-field"><div class="dfk">'+esc(k)+'</div><div class="dfv">'+esc(v)+'</div></div>').join('');}

/* ===== Overview ===== */
async function loadOverview(){
    try{
        const s=await api('/analytics/summary');
        document.getElementById('stats-cards').innerHTML=
            '<div class="card"><div class="lbl">Patients</div><div class="val">'+s.total_patients+'</div></div>'+
            '<div class="card"><div class="lbl">Doctors</div><div class="val">'+s.total_doctors+'</div></div>'+
            '<div class="card"><div class="lbl">Appointments</div><div class="val">'+s.total_appointments+'</div></div>'+
            '<div class="card green"><div class="lbl">Completed</div><div class="val">'+s.appointments_by_status.completed+'</div></div>'+
            '<div class="card amber"><div class="lbl">Scheduled</div><div class="val">'+s.appointments_by_status.scheduled+'</div></div>'+
            '<div class="card red"><div class="lbl">Cancelled</div><div class="val">'+s.appointments_by_status.cancelled+'</div></div>';
        const depts=s.patients_by_department,maxD=Math.max(...Object.values(depts),1);
        document.getElementById('dept-chart').innerHTML=Object.entries(depts).sort((a,b)=>b[1]-a[1]).map(([d,c])=>'<div class="bar-row"><div class="bar-lbl">'+esc(d)+'</div><div class="bar-track"><div class="bar-fill" style="width:'+(c/maxD)*100+'%;background:linear-gradient(90deg,var(--primary),#3b82f6)">'+c+'</div></div></div>').join('')||'<div class="empty">No data</div>';
        const st=s.appointments_by_status,maxS=Math.max(st.scheduled,st.completed,st.cancelled,1);
        document.getElementById('status-chart').innerHTML=[{l:'Scheduled',v:st.scheduled,c:'var(--blue)'},{l:'Completed',v:st.completed,c:'var(--green)'},{l:'Cancelled',v:st.cancelled,c:'var(--red)'}].map(x=>'<div class="bar-row"><div class="bar-lbl">'+x.l+'</div><div class="bar-track"><div class="bar-fill" style="width:'+(x.v/maxS)*100+'%;background:'+x.c+'">'+x.v+'</div></div></div>').join('');
    }catch(e){document.getElementById('stats-cards').innerHTML='<div class="empty">Analytics requires admin role</div>';}
    const recent=allPatients.slice(0,10);
    document.getElementById('recent-patients').innerHTML=recent.map(p=>'<tr><td><span class="clickable" onclick="showPatientDetail('+p.id+')">'+esc(p.name)+'</span></td><td>'+p.age+'</td><td>'+esc(p.gender)+'</td><td>'+esc(p.blood_group)+'</td><td>'+esc(p.contact)+'</td></tr>').join('')||'<tr><td colspan="5" class="empty">No patients</td></tr>';
}

/* ===== Patients ===== */
function renderPatients(){
    const q=(document.getElementById('patient-search').value||'').toLowerCase();
    let f=allPatients;
    if(q)f=f.filter(p=>p.name.toLowerCase().includes(q)||p.contact.includes(q)||(p.address||'').toLowerCase().includes(q)||(p.blood_group||'').toLowerCase().includes(q));
    const total=f.length,pages=Math.ceil(total/PAGE_SIZE)||1;
    if(patientPage>pages)patientPage=pages;
    const start=(patientPage-1)*PAGE_SIZE,slice=f.slice(start,start+PAGE_SIZE);
    document.getElementById('patients-count-label').textContent='All Patients ('+total+')';
    document.getElementById('patients-tbody').innerHTML=slice.map(p=>
        '<tr><td>'+p.id+'</td><td><span class="clickable" onclick="showPatientDetail('+p.id+')">'+esc(p.name)+'</span></td><td>'+p.age+'</td><td>'+esc(p.gender)+'</td><td>'+esc(p.contact)+'</td><td>'+esc(p.blood_group)+'</td><td>'+esc(p.address)+'</td></tr>'
    ).join('')||'<tr><td colspan="7" class="empty">No patients found</td></tr>';
    renderPagination('patients-pagination',patientPage,pages,p=>{patientPage=p;renderPatients();},total);
}
async function showPatientDetail(id){
    const p=allPatients.find(x=>x.id===id);if(!p)return;
    document.getElementById('patients-list-view').style.display='none';
    document.getElementById('patients-detail-view').style.display='block';
    document.getElementById('pd-name').textContent=p.name;
    document.getElementById('pd-fields').innerHTML=detailFields({'Patient ID':p.id,Age:p.age,Gender:p.gender,'Blood Group':p.blood_group||'-',Contact:p.contact,Address:p.address||'-',Status:p.is_active?'Active':'Inactive'});
    activateTab('patients');
    try{
        const recs=await api('/patients/'+id+'/records');
        document.getElementById('pd-records').innerHTML=recs.map(r=>'<tr><td>'+fmtDate(r.created_at)+'</td><td><span class="clickable" onclick="showDoctorDetail('+r.doctor_id+')">'+esc(doctorName(r.doctor_id))+'</span></td><td>'+esc(r.diagnosis)+'</td><td>'+esc(r.prescription)+'</td><td>'+esc(r.notes)+'</td></tr>').join('')||'<tr><td colspan="5" class="empty">No medical records</td></tr>';
    }catch(e){document.getElementById('pd-records').innerHTML='<tr><td colspan="5" class="empty">Access denied or error loading records</td></tr>';}
    const appts=allAppointments.filter(a=>a.patient_id===id);
    document.getElementById('pd-appointments').innerHTML=appts.map(a=>'<tr><td>'+fmtDate(a.date_time)+'</td><td><span class="clickable" onclick="showDoctorDetail('+a.doctor_id+')">'+esc(doctorName(a.doctor_id))+'</span></td><td>'+esc(a.reason)+'</td><td><span class="badge '+a.status+'">'+a.status+'</span></td></tr>').join('')||'<tr><td colspan="4" class="empty">No appointments</td></tr>';
}
function showPatientsList(){document.getElementById('patients-detail-view').style.display='none';document.getElementById('patients-list-view').style.display='block';renderPatients();}

/* ===== Doctors ===== */
function populateDeptFilter(){
    const depts=[...new Set(allDoctors.map(d=>d.department))].sort();
    document.getElementById('dept-filter').innerHTML='<option value="">All Departments ('+depts.length+')</option>'+depts.map(d=>'<option value="'+esc(d)+'">'+esc(d)+'</option>').join('');
}
function renderDoctors(){
    const q=(document.getElementById('doctor-search').value||'').toLowerCase();
    const dept=document.getElementById('dept-filter').value;
    let f=allDoctors;
    if(q)f=f.filter(d=>d.name.toLowerCase().includes(q)||d.specialization.toLowerCase().includes(q)||d.department.toLowerCase().includes(q));
    if(dept)f=f.filter(d=>d.department===dept);
    document.getElementById('doctors-count-label').textContent='All Doctors ('+f.length+')';
    document.getElementById('doctors-tbody').innerHTML=f.map(d=>
        '<tr><td>'+d.id+'</td><td><span class="clickable" onclick="showDoctorDetail('+d.id+')">'+esc(d.name)+'</span></td><td>'+esc(d.specialization)+'</td><td>'+esc(d.department)+'</td><td>'+esc(d.contact)+'</td></tr>'
    ).join('')||'<tr><td colspan="5" class="empty">No doctors found</td></tr>';
}
async function showDoctorDetail(id){
    const d=allDoctors.find(x=>x.id===id);if(!d)return;
    document.getElementById('doctors-list-view').style.display='none';
    document.getElementById('doctors-detail-view').style.display='block';
    document.getElementById('dd-name').textContent=d.name;
    document.getElementById('dd-fields').innerHTML=detailFields({'Doctor ID':d.id,Specialization:d.specialization,Department:d.department,Contact:d.contact});
    activateTab('doctors');
    const appts=allAppointments.filter(a=>a.doctor_id===id);
    document.getElementById('dd-appointments').innerHTML=appts.map(a=>'<tr><td>'+fmtDate(a.date_time)+'</td><td><span class="clickable" onclick="showPatientDetail('+a.patient_id+')">'+esc(patientName(a.patient_id))+'</span></td><td>'+esc(a.reason)+'</td><td><span class="badge '+a.status+'">'+a.status+'</span></td></tr>').join('')||'<tr><td colspan="4" class="empty">No appointments</td></tr>';
}
function showDoctorsList(){document.getElementById('doctors-detail-view').style.display='none';document.getElementById('doctors-list-view').style.display='block';renderDoctors();}

/* ===== Appointments ===== */
function filterAppointments(){apptPage=1;renderAppointments();}
function renderAppointments(){
    const q=(document.getElementById('appt-search').value||'').toLowerCase();
    const st=document.getElementById('appt-status-filter').value;
    let f=allAppointments;
    if(q)f=f.filter(a=>(a.reason||'').toLowerCase().includes(q)||patientName(a.patient_id).toLowerCase().includes(q)||doctorName(a.doctor_id).toLowerCase().includes(q));
    if(st)f=f.filter(a=>a.status===st);
    const total=f.length,pages=Math.ceil(total/PAGE_SIZE)||1;
    if(apptPage>pages)apptPage=pages;
    const start=(apptPage-1)*PAGE_SIZE,slice=f.slice(start,start+PAGE_SIZE);
    document.getElementById('appts-count-label').textContent='All Appointments ('+total+')';
    document.getElementById('appts-tbody').innerHTML=slice.map(a=>
        '<tr><td>'+a.id+'</td><td><span class="clickable" onclick="showPatientDetail('+a.patient_id+')">'+esc(patientName(a.patient_id))+'</span></td><td><span class="clickable" onclick="showDoctorDetail('+a.doctor_id+')">'+esc(doctorName(a.doctor_id))+'</span></td><td>'+fmtDate(a.date_time)+'</td><td>'+esc(a.reason)+'</td><td><span class="badge '+a.status+'">'+a.status+'</span></td></tr>'
    ).join('')||'<tr><td colspan="6" class="empty">No appointments found</td></tr>';
    renderPagination('appts-pagination',apptPage,pages,p=>{apptPage=p;renderAppointments();},total);
}

/* ===== Pagination ===== */
function renderPagination(elId,current,total,onPage,count){
    const el=document.getElementById(elId);
    if(total<=1){el.innerHTML=count?'<span class="pg-info">'+count+' records</span>':'';return;}
    let h='<span class="pg-info">'+count+' records</span>';
    h+='<button class="pg-btn" id="'+elId+'-prev" '+(current<=1?'disabled':'')+'>&#171; Prev</button>';
    let s=Math.max(1,current-2),e=Math.min(total,s+4);
    if(e-s<4)s=Math.max(1,e-4);
    for(let i=s;i<=e;i++)h+='<button class="pg-btn '+(i===current?'active':'')+'" data-pg="'+i+'">'+i+'</button>';
    h+='<button class="pg-btn" id="'+elId+'-next" '+(current>=total?'disabled':'')+'>Next &#187;</button>';
    el.innerHTML=h;
    el.querySelector('#'+elId+'-prev').addEventListener('click',()=>{if(current>1)onPage(current-1);});
    el.querySelector('#'+elId+'-next').addEventListener('click',()=>{if(current<total)onPage(current+1);});
    el.querySelectorAll('[data-pg]').forEach(b=>b.addEventListener('click',()=>onPage(parseInt(b.dataset.pg))));
}
</script>
</body>
</html>
"""
