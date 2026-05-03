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
<title>Healthcare DMS — Dashboard</title>
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
.header { background:linear-gradient(135deg,var(--primary),#16213e); color:#fff; padding:16px 28px; display:flex; justify-content:space-between; align-items:center; position:sticky; top:0; z-index:100; }
.header h1 { font-size:1.25rem; font-weight:600; }
.header .right { display:flex; align-items:center; gap:14px; }
.header .user-info { font-size:.85rem; opacity:.85; }
.hbtn { background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.25); color:#fff; padding:5px 14px; border-radius:6px; cursor:pointer; font-size:.82rem; }
.hbtn:hover { background:rgba(255,255,255,.22); }
.nav { background:#fff; border-bottom:1px solid var(--gray-200); padding:0 28px; display:flex; gap:0; }
.nav-tab { padding:12px 20px; font-size:.9rem; cursor:pointer; border-bottom:3px solid transparent; color:var(--gray-500); font-weight:500; transition:all .15s; user-select:none; }
.nav-tab:hover { color:var(--primary); background:var(--gray-50); }
.nav-tab.active { color:var(--primary); border-bottom-color:var(--primary); font-weight:600; }
.container { max-width:1240px; margin:0 auto; padding:20px 24px; }
.page { display:none; }
.page.active { display:block; }
.stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:14px; margin-bottom:24px; }
.card { background:#fff; border-radius:var(--radius); padding:20px; box-shadow:var(--shadow); }
.card .lbl { font-size:.78rem; color:var(--gray-500); text-transform:uppercase; letter-spacing:.4px; margin-bottom:4px; }
.card .val { font-size:1.8rem; font-weight:700; color:var(--primary); }
.card.green .val { color:var(--green); }
.card.amber .val { color:var(--amber); }
.card.red .val { color:var(--red); }
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
.badge.admin { background:var(--red-bg); color:var(--red); }
.badge.doctor { background:var(--green-bg); color:var(--green); }
.badge.receptionist { background:var(--blue-bg); color:var(--blue); }
.empty { text-align:center; padding:30px; color:var(--gray-400); }
.bars { display:flex; flex-direction:column; gap:8px; }
.bar-row { display:flex; align-items:center; gap:10px; }
.bar-lbl { min-width:100px; font-size:.85rem; text-align:right; color:var(--gray-700); }
.bar-track { flex:1; background:var(--gray-200); border-radius:6px; height:26px; overflow:hidden; }
.bar-fill { height:100%; border-radius:6px; display:flex; align-items:center; padding-left:10px; color:#fff; font-size:.78rem; font-weight:600; min-width:28px; transition:width .5s ease; }
.grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-bottom:18px; }
.detail-panel { background:#fff; border-radius:var(--radius); padding:28px; box-shadow:var(--shadow); }
.detail-panel h2 { color:var(--primary); margin-bottom:18px; font-size:1.3rem; }
.detail-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px 24px; margin-bottom:20px; }
.detail-field .dfk { font-size:.76rem; color:var(--gray-500); text-transform:uppercase; letter-spacing:.3px; }
.detail-field .dfv { font-size:1rem; font-weight:500; margin-top:2px; }
.back-btn { display:inline-flex; align-items:center; gap:6px; color:var(--primary); cursor:pointer; font-size:.9rem; font-weight:500; margin-bottom:16px; user-select:none; }
.back-btn:hover { text-decoration:underline; }
.login-wrap { display:flex; justify-content:center; align-items:center; min-height:90vh; }
.login-box { background:#fff; padding:36px; border-radius:12px; box-shadow:0 4px 24px rgba(0,0,0,.08); width:340px; }
.login-box h2 { margin-bottom:20px; text-align:center; color:var(--primary); font-size:1.3rem; }
.login-box input { width:100%; padding:10px 14px; margin-bottom:12px; border:1px solid var(--gray-200); border-radius:8px; font-size:.92rem; }
.login-box button { width:100%; padding:10px; background:var(--primary); color:#fff; border:none; border-radius:8px; font-size:.95rem; cursor:pointer; font-weight:500; }
.login-box button:hover { background:var(--primary-light); }
.login-box .err { color:var(--red); font-size:.83rem; margin-bottom:8px; text-align:center; }
.pagination { display:flex; justify-content:center; align-items:center; gap:8px; margin-top:14px; padding-top:10px; }
.pg-btn { padding:6px 12px; border:1px solid var(--gray-200); border-radius:6px; font-size:.84rem; cursor:pointer; background:#fff; }
.pg-btn:hover { background:var(--gray-50); }
.pg-btn.active { background:var(--primary); color:#fff; border-color:var(--primary); }
.pg-btn:disabled { opacity:.4; cursor:default; }
.pg-info { font-size:.84rem; color:var(--gray-500); }
/* Buttons */
.btn { padding:7px 16px; border:none; border-radius:6px; font-size:.85rem; cursor:pointer; font-weight:500; transition:background .15s; }
.btn-primary { background:var(--primary); color:#fff; }
.btn-primary:hover { background:var(--primary-light); }
.btn-success { background:var(--green); color:#fff; }
.btn-success:hover { background:#047857; }
.btn-danger { background:var(--red); color:#fff; }
.btn-danger:hover { background:#b91c1c; }
.btn-sm { padding:4px 10px; font-size:.78rem; }
/* Modal */
.modal-overlay { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,.45); z-index:200; justify-content:center; align-items:center; }
.modal-overlay.show { display:flex; }
.modal { background:#fff; border-radius:12px; padding:28px; width:420px; max-width:90vw; max-height:85vh; overflow-y:auto; box-shadow:0 8px 32px rgba(0,0,0,.18); }
.modal h3 { color:var(--primary); margin-bottom:16px; font-size:1.1rem; }
.modal label { display:block; font-size:.82rem; color:var(--gray-700); margin-bottom:4px; font-weight:500; }
.modal input,.modal select,.modal textarea { width:100%; padding:8px 12px; border:1px solid var(--gray-200); border-radius:6px; font-size:.9rem; margin-bottom:12px; outline:none; font-family:inherit; }
.modal input:focus,.modal select:focus,.modal textarea:focus { border-color:var(--primary); box-shadow:0 0 0 2px var(--primary-bg); }
.modal textarea { resize:vertical; min-height:60px; }
.modal .btn-row { display:flex; justify-content:flex-end; gap:10px; margin-top:8px; }
.modal .err { color:var(--red); font-size:.83rem; margin-bottom:8px; }
.toast { position:fixed; top:20px; right:20px; padding:12px 20px; border-radius:8px; color:#fff; font-size:.88rem; z-index:300; opacity:0; transition:opacity .3s; pointer-events:none; }
.toast.show { opacity:1; }
.toast.success { background:var(--green); }
.toast.error { background:var(--red); }
.action-btns { display:flex; gap:6px; }
@media(max-width:768px) { .grid-2{grid-template-columns:1fr;} .detail-grid{grid-template-columns:1fr;} .search-box{width:100%!important;} .nav{overflow-x:auto;} .modal{width:95vw;} }
</style>
</head>
<body>

<!-- TOAST -->
<div id="toast" class="toast"></div>

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

<!-- APP -->
<div id="app" style="display:none">
<div class="header">
    <h1>
        <a href="#" onclick="activateTab('overview'); return false;" style="color: inherit; text-decoration: none;">
            &#9764; Healthcare DMS
        </a>
    </h1>    <div class="right">
        <span class="user-info" id="user-label"></span>
        <button class="hbtn" onclick="logout()">Logout</button>
    </div>
</div>
<div class="nav" id="nav">
    <div class="nav-tab active" data-page="overview">Overview</div>
    <div class="nav-tab" data-page="patients">Patients</div>
    <div class="nav-tab" data-page="doctors">Doctors</div>
    <div class="nav-tab" data-page="appointments">Appointments</div>
    <div class="nav-tab" data-page="users">Users</div>
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
                <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
                    <input class="search-box" id="patient-search" placeholder="Search name, contact, address..." oninput="debouncedSearchPatients()">
                    <button class="btn btn-success" onclick="openModal('patient-modal')">+ Add Patient</button>
                </div>
            </div>
            <table><thead><tr><th>ID</th><th>Name</th><th>Age</th><th>Gender</th><th>Contact</th><th>Blood</th><th>Actions</th></tr></thead>
            <tbody id="patients-tbody"></tbody></table>
            <div id="patients-pagination" class="pagination"></div>
        </div>
    </div>
    <div id="patients-detail-view" style="display:none">
        <div class="detail-panel">
            <div class="back-btn" onclick="showPatientsList()">&#8592; Back to Patients</div>
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap">
                <h2 id="pd-name"></h2>
                <div class="action-btns">
                    <button class="btn btn-primary btn-sm" id="pd-edit-btn">Edit</button>
                    <button class="btn btn-danger btn-sm" id="pd-delete-btn">Delete</button>
                </div>
            </div>
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
                <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
                    <input class="search-box" id="doctor-search" placeholder="Search name, specialization..." oninput="debouncedSearchDoctors()" style="width:220px">
                    <select class="search-box" id="dept-filter" onchange="renderDoctors()" style="width:170px"><option value="">All Departments</option></select>
                    <button class="btn btn-success" onclick="openModal('doctor-modal')">+ Add Doctor</button>
                </div>
            </div>
            <table><thead><tr><th>ID</th><th>Name</th><th>Specialization</th><th>Department</th><th>Contact</th><th>Actions</th></tr></thead>
            <tbody id="doctors-tbody"></tbody></table>
        </div>
    </div>
    <div id="doctors-detail-view" style="display:none">
        <div class="detail-panel">
            <div class="back-btn" onclick="showDoctorsList()">&#8592; Back to Doctors</div>
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap">
                <h2 id="dd-name"></h2>
                <div class="action-btns">
                    <button class="btn btn-primary btn-sm" id="dd-edit-btn">Edit</button>
                    <button class="btn btn-danger btn-sm" id="dd-delete-btn">Delete</button>
                </div>
            </div>
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
            <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
                <input class="search-box" id="appt-search" placeholder="Search patient, doctor, reason..." oninput="debouncedFilterAppts()" style="width:220px">
                <select class="search-box" id="appt-status-filter" onchange="filterAppointments()" style="width:150px">
                    <option value="">All Statuses</option><option value="scheduled">Scheduled</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option>
                </select>
                <button class="btn btn-success" onclick="openAddApptModal()">+ Add Appointment</button>
            </div>
        </div>
        <table><thead><tr><th>ID</th><th>Patient</th><th>Doctor</th><th>Date &amp; Time</th><th>Reason</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody id="appts-tbody"></tbody></table>
        <div id="appts-pagination" class="pagination"></div>
    </div>
</div>

<!-- USERS -->
<div id="pg-users" class="page">
    <div class="section">
        <div class="section-head">
            <h3 id="users-count-label">All Users</h3>
            <button class="btn btn-success" onclick="openModal('user-modal')">+ Add User</button>
        </div>
        <table><thead><tr><th>ID</th><th>Username</th><th>Full Name</th><th>Role</th></tr></thead>
        <tbody id="users-tbody"></tbody></table>
    </div>
</div>

</div></div>

<!-- ===== MODALS ===== -->

<!-- Add/Edit Patient Modal -->
<div id="patient-modal" class="modal-overlay">
<div class="modal">
    <h3 id="patient-modal-title">Add New Patient</h3>
    <div id="patient-modal-err" class="err" style="display:none"></div>
    <input type="hidden" id="pm-id">
    <label>Name *</label><input id="pm-name" placeholder="Full name">
    <label>Age *</label><input id="pm-age" type="number" placeholder="Age" min="0" max="150">
    <label>Gender *</label><select id="pm-gender"><option value="Male">Male</option><option value="Female">Female</option><option value="Other">Other</option></select>
    <label>Contact *</label><input id="pm-contact" placeholder="Phone number">
    <label>Address</label><input id="pm-address" placeholder="Address">
    <label>Blood Group</label><select id="pm-blood"><option value="">Select</option><option>A+</option><option>A-</option><option>B+</option><option>B-</option><option>AB+</option><option>AB-</option><option>O+</option><option>O-</option></select>
    <div class="btn-row">
        <button class="btn" style="background:var(--gray-200)" onclick="closeModal('patient-modal')">Cancel</button>
        <button class="btn btn-primary" onclick="savePatient()">Save</button>
    </div>
</div></div>

<!-- Add/Edit Doctor Modal -->
<div id="doctor-modal" class="modal-overlay">
<div class="modal">
    <h3 id="doctor-modal-title">Add New Doctor</h3>
    <div id="doctor-modal-err" class="err" style="display:none"></div>
    <input type="hidden" id="dm-id">
    <label>Name *</label><input id="dm-name" placeholder="Dr. Full Name">
    <label>Specialization *</label><input id="dm-spec" placeholder="e.g. Cardiologist">
    <label>Department *</label><input id="dm-dept" placeholder="e.g. Cardiology">
    <label>Contact *</label><input id="dm-contact" placeholder="Phone number">
    <div class="btn-row">
        <button class="btn" style="background:var(--gray-200)" onclick="closeModal('doctor-modal')">Cancel</button>
        <button class="btn btn-primary" onclick="saveDoctor()">Save</button>
    </div>
</div></div>

<!-- Add User Modal -->
<div id="user-modal" class="modal-overlay">
<div class="modal">
    <h3>Add New User</h3>
    <div id="user-modal-err" class="err" style="display:none"></div>
    <label>Username *</label><input id="um-username" placeholder="Username">
    <label>Password *</label><input id="um-password" type="password" placeholder="Password">
    <label>Full Name *</label><input id="um-fullname" placeholder="Full name">
    <label>Role *</label><select id="um-role"><option value="receptionist">Receptionist</option><option value="doctor">Doctor</option><option value="admin">Admin</option></select>
    <div class="btn-row">
        <button class="btn" style="background:var(--gray-200)" onclick="closeModal('user-modal')">Cancel</button>
        <button class="btn btn-primary" onclick="saveUser()">Save</button>
    </div>
</div></div>

<!-- Add Appointment Modal -->
<div id="appt-modal" class="modal-overlay">
<div class="modal">
    <h3>Add New Appointment</h3>
    <div id="appt-modal-err" class="err" style="display:none"></div>
    <label>Patient *</label><select id="am-patient"></select>
    <label>Doctor *</label><select id="am-doctor"></select>
    <label>Date &amp; Time *</label><input id="am-datetime" type="datetime-local">
    <label>Reason</label><textarea id="am-reason" placeholder="Reason for visit"></textarea>
    <div class="btn-row">
        <button class="btn" style="background:var(--gray-200)" onclick="closeModal('appt-modal')">Cancel</button>
        <button class="btn btn-primary" onclick="saveAppointment()">Save</button>
    </div>
</div></div>

<!-- Status Change Modal -->
<div id="status-modal" class="modal-overlay">
<div class="modal">
    <h3>Update Appointment Status</h3>
    <input type="hidden" id="sm-id">
    <label>Status</label>
    <select id="sm-status"><option value="scheduled">Scheduled</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option></select>
    <div class="btn-row">
        <button class="btn" style="background:var(--gray-200)" onclick="closeModal('status-modal')">Cancel</button>
        <button class="btn btn-primary" onclick="changeApptStatus()">Update</button>
    </div>
</div></div>

<!-- Add Medical Record Modal -->
<div id="record-modal" class="modal-overlay">
<div class="modal">
    <h3>Add Medical Record</h3>
    <div id="record-modal-err" class="err" style="display:none"></div>
    <div style="font-size:.83rem;color:var(--gray-500);margin-bottom:12px" id="record-modal-meta"></div>
    <label>Diagnosis *</label><input id="rm-diagnosis" placeholder="Primary diagnosis">
    <label>Prescription</label><textarea id="rm-prescription" placeholder="Medication and dosage"></textarea>
    <label>Notes</label><textarea id="rm-notes" placeholder="Additional notes"></textarea>
    <label>Upload File (PDF/image) *</label><input id="rm-file" type="file" accept=".pdf,.jpg,.jpeg,.png">
    <div class="btn-row">
        <button class="btn" style="background:var(--gray-200)" onclick="closeModal('record-modal')">Cancel</button>
        <button class="btn btn-primary" onclick="saveMedicalRecordFromAppointment()">Save Record</button>
    </div>
</div></div>

<script>
/* ===== State ===== */
const API='';
let TOKEN='',ROLE='',CURRENT_USER='';
let allPatients=[],allDoctors=[],allAppointments=[],allUsers=[];
const PAGE_SIZE=15;
let patientPage=1,apptPage=1;
let selectedRecordApptId = null;
let selectedRecordPatientId = null;

/* ===== Helpers ===== */
const _e=document.createElement('div');
function esc(s){if(s==null)return'';_e.textContent=String(s);return _e.innerHTML;}
function debounce(fn,ms){let t;return(...a)=>{clearTimeout(t);t=setTimeout(()=>fn(...a),ms);};}
const debouncedSearchPatients=debounce(()=>{patientPage=1;renderPatients();},250);
const debouncedSearchDoctors=debounce(renderDoctors,250);
const debouncedFilterAppts=debounce(()=>{apptPage=1;renderAppointments();},250);

function toast(msg,type){const t=document.getElementById('toast');t.textContent=msg;t.className='toast '+type+' show';setTimeout(()=>t.classList.remove('show'),3000);}
function hdr(){return{'Authorization':'Bearer '+TOKEN,'Content-Type':'application/json'};}
async function api(path){const r=await fetch(API+path,{headers:hdr()});if(!r.ok)throw new Error(r.status);return r.json();}
async function apiPost(path,body){const r=await fetch(API+path,{method:'POST',headers:hdr(),body:JSON.stringify(body)});if(!r.ok){const e=await r.json().catch(()=>({}));throw new Error(e.detail||r.statusText);}return r.json();}
async function apiPut(path,body){const r=await fetch(API+path,{method:'PUT',headers:hdr(),body:JSON.stringify(body)});if(!r.ok){const e=await r.json().catch(()=>({}));throw new Error(e.detail||r.statusText);}return r.json();}
async function apiPatch(path,body){const r=await fetch(API+path,{method:'PATCH',headers:hdr(),body:JSON.stringify(body)});if(!r.ok){const e=await r.json().catch(()=>({}));throw new Error(e.detail||r.statusText);}return r.json();}
async function apiDelete(path){const r=await fetch(API+path,{method:'DELETE',headers:hdr()});if(!r.ok){const e=await r.json().catch(()=>({}));throw new Error(e.detail||r.statusText);}}

function openModal(id){document.getElementById(id).classList.add('show');}
function closeModal(id){document.getElementById(id).classList.remove('show');}
function doctorName(id){const d=allDoctors.find(x=>x.id===id);return d?d.name:'Doctor #'+id;}
function patientName(id){const p=allPatients.find(x=>x.id===id);return p?p.name:'Patient #'+id;}
function fmtDate(s){if(!s)return'-';const d=new Date(s);return d.toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'})+' '+d.toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit'});}
function detailFields(obj){return Object.entries(obj).map(([k,v])=>'<div class="detail-field"><div class="dfk">'+esc(k)+'</div><div class="dfv">'+esc(v)+'</div></div>').join('');}

/* ===== Auth ===== */
async function doLogin(){
    const u=document.getElementById('username').value,p=document.getElementById('password').value;
    const err=document.getElementById('login-error');err.style.display='none';
    try{
        const r=await fetch(API+'/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
        if(!r.ok){err.textContent='Invalid credentials';err.style.display='block';return;}
        const data = await r.json();
        TOKEN = data.access_token;
        localStorage.setItem('hc_token', TOKEN); 

        document.getElementById('login-screen').style.display='none';
        document.getElementById('app').style.display='block';
        initApp();
    }catch(e){err.textContent='Server unreachable';err.style.display='block';}
}
function logout(){
    TOKEN='';
    ROLE='';
    localStorage.removeItem('hc_token');
    document.getElementById('app').style.display='none';
    document.getElementById('login-screen').style.display='block';
    }
document.getElementById('password').addEventListener('keydown',e=>{if(e.key==='Enter')doLogin();});

/* ===== Nav ===== */
document.querySelectorAll('.nav-tab').forEach(tab=>{
    tab.addEventListener('click',()=>{
        const pageName = tab.dataset.page;
        localStorage.setItem('hc_current_page', pageName);

        document.querySelectorAll('.nav-tab').forEach(t=>t.classList.remove('active'));
        document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById('pg-'+pageName).classList.add('active');
        
        if(pageName==='patients') renderPatients();
        if(pageName==='doctors') renderDoctors();
        if(pageName==='appointments') renderAppointments();
        if(pageName==='users') renderUsers();
        if(pageName==='overview') loadOverview(); 
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
    try {
        const me = await api('/auth/me');
        ROLE = me.role;
        CURRENT_USER = me.username;
        document.getElementById('user-label').textContent = me.full_name + ' (' + me.role + ')';
    } catch(e) {
        // If the token is expired or invalid, force a logout
        logout();
        return;
    }

    // Show/hide admin-only features
    const isAdmin = ROLE === 'admin';
    document.querySelectorAll('.admin-only').forEach(el => el.style.display = isAdmin ? '' : 'none');
    const usersTab = document.querySelector('.nav-tab[data-page="users"]');
    if(usersTab) usersTab.style.display = isAdmin ? '' : 'none';

    await Promise.all([loadPatients(), loadDoctors(), loadAppointments(), loadUsers()]);
    const savedPage = localStorage.getItem('hc_current_page') || 'overview';
    
    activateTab(savedPage);
    
    if (savedPage === 'overview') loadOverview();
    else if (savedPage === 'patients') renderPatients();
    else if (savedPage === 'doctors') renderDoctors();
    else if (savedPage === 'appointments') renderAppointments();
    else if (savedPage === 'users') renderUsers();
}
async function loadPatients(){try{allPatients=await api('/patients/');}catch(e){allPatients=[];}}
async function loadDoctors(){try{allDoctors=await api('/doctors/');}catch(e){allDoctors=[];} populateDeptFilter();}
async function loadAppointments(){try{allAppointments=await api('/appointments/');}catch(e){allAppointments=[];}}
async function loadUsers(){try{allUsers=await api('/auth/users');}catch(e){allUsers=[];}}

/* ===== Overview ===== */
async function loadOverview(){
    try{
        const s=await api('/analytics/summary');
        document.getElementById('stats-cards').innerHTML=
            '<div class="card"><div class="lbl">Patients</div><div class="val">'+s.total_patients+'</div></div>'+
            '<div class="card"><div class="lbl">Doctors</div><div class="val">'+s.total_doctors+'</div></div>'+
            '<div class="card"><div class="lbl">Appointments</div><div class="val">'+s.total_appointments+'</div></div>'+
            '<div class="card green"><div class="lbl">Completed</div><div class="val">'+(s.appointments_by_status.completed||0)+'</div></div>'+
            '<div class="card amber"><div class="lbl">Scheduled</div><div class="val">'+(s.appointments_by_status.scheduled||0)+'</div></div>'+
            '<div class="card red"><div class="lbl">Cancelled</div><div class="val">'+(s.appointments_by_status.cancelled||0)+'</div></div>';
        const depts=s.patients_by_department||{},maxD=Math.max(...Object.values(depts),1);
        document.getElementById('dept-chart').innerHTML=Object.entries(depts).sort((a,b)=>b[1]-a[1]).map(([d,c])=>'<div class="bar-row"><div class="bar-lbl">'+esc(d)+'</div><div class="bar-track"><div class="bar-fill" style="width:'+(c/maxD)*100+'%;background:linear-gradient(90deg,var(--primary),#3b82f6)">'+c+'</div></div></div>').join('')||'<div class="empty">No data</div>';
        const st=s.appointments_by_status||{},maxS=Math.max(st.scheduled||0,st.completed||0,st.cancelled||0,1);
        document.getElementById('status-chart').innerHTML=[{l:'Scheduled',v:st.scheduled||0,c:'var(--blue)'},{l:'Completed',v:st.completed||0,c:'var(--green)'},{l:'Cancelled',v:st.cancelled||0,c:'var(--red)'}].map(x=>'<div class="bar-row"><div class="bar-lbl">'+x.l+'</div><div class="bar-track"><div class="bar-fill" style="width:'+(x.v/maxS)*100+'%;background:'+x.c+'">'+x.v+'</div></div></div>').join('');
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
        '<tr><td>'+p.id+'</td><td><span class="clickable" onclick="showPatientDetail('+p.id+')">'+esc(p.name)+'</span></td><td>'+p.age+'</td><td>'+esc(p.gender)+'</td><td>'+esc(p.contact)+'</td><td>'+esc(p.blood_group)+'</td><td><div class="action-btns"><button class="btn btn-primary btn-sm" onclick="openEditPatient('+p.id+')">Edit</button><button class="btn btn-danger btn-sm" onclick="deletePatient('+p.id+')">Del</button></div></td></tr>'
    ).join('')||'<tr><td colspan="7" class="empty">No patients found</td></tr>';
    renderPagination('patients-pagination',patientPage,pages,p=>{patientPage=p;renderPatients();},total);
}
async function showPatientDetail(id){
    const p=allPatients.find(x=>x.id===id);if(!p)return;
    document.getElementById('patients-list-view').style.display='none';
    document.getElementById('patients-detail-view').style.display='block';
    document.getElementById('pd-name').textContent=p.name;
    document.getElementById('pd-fields').innerHTML=detailFields({'Patient ID':p.id,Age:p.age,Gender:p.gender,'Blood Group':p.blood_group||'-',Contact:p.contact,Address:p.address||'-',Status:p.is_active?'Active':'Inactive'});
    document.getElementById('pd-edit-btn').onclick=()=>openEditPatient(id);
    document.getElementById('pd-delete-btn').onclick=()=>{deletePatient(id);showPatientsList();};
    activateTab('patients');
    try{
        const recs=await api('/patients/'+id+'/records');
        document.getElementById('pd-records').innerHTML=recs.map(r=>'<tr><td>'+fmtDate(r.created_at)+'</td><td><span class="clickable" onclick="showDoctorDetail('+r.doctor_id+')">'+esc(doctorName(r.doctor_id))+'</span></td><td>'+esc(r.diagnosis)+'</td><td>'+esc(r.prescription)+'</td><td>'+esc(r.notes)+'</td></tr>').join('')||'<tr><td colspan="5" class="empty">No medical records</td></tr>';
    }catch(e){document.getElementById('pd-records').innerHTML='<tr><td colspan="5" class="empty">Access denied or error</td></tr>';}
    const appts=allAppointments.filter(a=>a.patient_id===id);
    document.getElementById('pd-appointments').innerHTML=appts.map(a=>'<tr><td>'+fmtDate(a.date_time)+'</td><td><span class="clickable" onclick="showDoctorDetail('+a.doctor_id+')">'+esc(doctorName(a.doctor_id))+'</span></td><td>'+esc(a.reason)+'</td><td><span class="badge '+a.status+'">'+a.status+'</span></td></tr>').join('')||'<tr><td colspan="4" class="empty">No appointments</td></tr>';
}
function showPatientsList(){document.getElementById('patients-detail-view').style.display='none';document.getElementById('patients-list-view').style.display='block';renderPatients();}

function openEditPatient(id){
    const p=allPatients.find(x=>x.id===id);if(!p)return;
    document.getElementById('patient-modal-title').textContent='Edit Patient';
    document.getElementById('pm-id').value=p.id;
    document.getElementById('pm-name').value=p.name;
    document.getElementById('pm-age').value=p.age;
    document.getElementById('pm-gender').value=p.gender;
    document.getElementById('pm-contact').value=p.contact;
    document.getElementById('pm-address').value=p.address||'';
    document.getElementById('pm-blood').value=p.blood_group||'';
    document.getElementById('patient-modal-err').style.display='none';
    openModal('patient-modal');
}
async function savePatient(){
    const err=document.getElementById('patient-modal-err');err.style.display='none';
    const id=document.getElementById('pm-id').value;
    const name=document.getElementById('pm-name').value.trim();
    const age=parseInt(document.getElementById('pm-age').value);
    const gender=document.getElementById('pm-gender').value;
    const contact=document.getElementById('pm-contact').value.trim();
    const address=document.getElementById('pm-address').value.trim();
    const blood_group=document.getElementById('pm-blood').value;
    if(!name||!age||!contact){err.textContent='Name, age, and contact are required';err.style.display='block';return;}
    try{
        if(id){
            await apiPut('/patients/'+id,{name,age,gender,contact,address,blood_group});
            toast('Patient updated','success');
        }else{
            await apiPost('/patients/',{name,age,gender,contact,address,blood_group});
            toast('Patient created','success');
        }
        closeModal('patient-modal');
        await loadPatients();renderPatients();loadOverview();
    }catch(e){err.textContent=e.message;err.style.display='block';}
}
async function deletePatient(id){
    if(!confirm('Delete this patient?'))return;
    try{await apiDelete('/patients/'+id);toast('Patient deleted','success');await loadPatients();renderPatients();loadOverview();}
    catch(e){toast('Error: '+e.message,'error');}
}

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
        '<tr><td>'+d.id+'</td><td><span class="clickable" onclick="showDoctorDetail('+d.id+')">'+esc(d.name)+'</span></td><td>'+esc(d.specialization)+'</td><td>'+esc(d.department)+'</td><td>'+esc(d.contact)+'</td><td><div class="action-btns"><button class="btn btn-primary btn-sm" onclick="openEditDoctor('+d.id+')">Edit</button><button class="btn btn-danger btn-sm" onclick="deleteDoctor('+d.id+')">Del</button></div></td></tr>'
    ).join('')||'<tr><td colspan="6" class="empty">No doctors found</td></tr>';
}
async function showDoctorDetail(id){
    const d=allDoctors.find(x=>x.id===id);if(!d)return;
    document.getElementById('doctors-list-view').style.display='none';
    document.getElementById('doctors-detail-view').style.display='block';
    document.getElementById('dd-name').textContent=d.name;
    document.getElementById('dd-fields').innerHTML=detailFields({'Doctor ID':d.id,Specialization:d.specialization,Department:d.department,Contact:d.contact});
    document.getElementById('dd-edit-btn').onclick=()=>openEditDoctor(id);
    document.getElementById('dd-delete-btn').onclick=()=>{deleteDoctor(id);showDoctorsList();};
    activateTab('doctors');
    const appts=allAppointments.filter(a=>a.doctor_id===id);
    document.getElementById('dd-appointments').innerHTML=appts.map(a=>'<tr><td>'+fmtDate(a.date_time)+'</td><td><span class="clickable" onclick="showPatientDetail('+a.patient_id+')">'+esc(patientName(a.patient_id))+'</span></td><td>'+esc(a.reason)+'</td><td><span class="badge '+a.status+'">'+a.status+'</span></td></tr>').join('')||'<tr><td colspan="4" class="empty">No appointments</td></tr>';
}
function showDoctorsList(){document.getElementById('doctors-detail-view').style.display='none';document.getElementById('doctors-list-view').style.display='block';renderDoctors();}

function openEditDoctor(id){
    const d=allDoctors.find(x=>x.id===id);if(!d)return;
    document.getElementById('doctor-modal-title').textContent='Edit Doctor';
    document.getElementById('dm-id').value=d.id;
    document.getElementById('dm-name').value=d.name;
    document.getElementById('dm-spec').value=d.specialization;
    document.getElementById('dm-dept').value=d.department;
    document.getElementById('dm-contact').value=d.contact;
    document.getElementById('doctor-modal-err').style.display='none';
    openModal('doctor-modal');
}
async function saveDoctor(){
    const err=document.getElementById('doctor-modal-err');err.style.display='none';
    const id=document.getElementById('dm-id').value;
    const name=document.getElementById('dm-name').value.trim();
    const specialization=document.getElementById('dm-spec').value.trim();
    const department=document.getElementById('dm-dept').value.trim();
    const contact=document.getElementById('dm-contact').value.trim();
    if(!name||!specialization||!department||!contact){err.textContent='All fields are required';err.style.display='block';return;}
    try{
        if(id){
            await apiPut('/doctors/'+id,{name,specialization,department,contact});
            toast('Doctor updated','success');
        }else{
            await apiPost('/doctors/',{name,specialization,department,contact});
            toast('Doctor created','success');
        }
        closeModal('doctor-modal');
        await loadDoctors();renderDoctors();loadOverview();
    }catch(e){err.textContent=e.message;err.style.display='block';}
}
async function deleteDoctor(id){
    if(!confirm('Delete this doctor?'))return;
    try{await apiDelete('/doctors/'+id);toast('Doctor deleted','success');await loadDoctors();renderDoctors();loadOverview();}
    catch(e){toast('Error: '+e.message,'error');}
}

/* ===== Users ===== */
function renderUsers(){
    document.getElementById('users-count-label').textContent='All Users ('+allUsers.length+')';
    document.getElementById('users-tbody').innerHTML=allUsers.map(u=>
        '<tr><td>'+u.id+'</td><td>'+esc(u.username)+'</td><td>'+esc(u.full_name)+'</td><td><span class="badge '+u.role+'">'+esc(u.role)+'</span></td></tr>'
    ).join('')||'<tr><td colspan="4" class="empty">No users</td></tr>';
}
async function saveUser(){
    const err=document.getElementById('user-modal-err');err.style.display='none';
    const username=document.getElementById('um-username').value.trim();
    const password=document.getElementById('um-password').value;
    const full_name=document.getElementById('um-fullname').value.trim();
    const role=document.getElementById('um-role').value;
    if(!username||!password||!full_name){err.textContent='All fields are required';err.style.display='block';return;}
    try{
        await apiPost('/auth/register',{username,password,full_name,role});
        toast('User created','success');
        closeModal('user-modal');
        document.getElementById('um-username').value='';document.getElementById('um-password').value='';document.getElementById('um-fullname').value='';
        await loadUsers();renderUsers();
    }catch(e){err.textContent=e.message;err.style.display='block';}
}

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
    const canAddRecord = ROLE === 'admin' || ROLE === 'doctor';
    document.getElementById('appts-tbody').innerHTML=slice.map(a=>
        '<tr><td>'+a.id+'</td>'+
        '<td><span class="clickable" onclick="showPatientDetail('+a.patient_id+')">'+esc(patientName(a.patient_id))+'</span></td>'+
        '<td><span class="clickable" onclick="showDoctorDetail('+a.doctor_id+')">'+esc(doctorName(a.doctor_id))+'</span></td>'+
        '<td>'+fmtDate(a.date_time)+'</td><td>'+esc(a.reason)+'</td>'+
        '<td><span class="badge '+a.status+'" style="cursor:pointer" onclick="openStatusModal('+a.id+',\''+a.status+'\')">'+a.status+'</span></td>'+
        '<td><div class="action-btns">'+(canAddRecord ? '<button class="btn btn-primary btn-sm" onclick="openRecordModal('+a.id+','+a.patient_id+','+a.doctor_id+')">Add Record</button>' : '')+'<button class="btn btn-danger btn-sm" onclick="deleteAppointment('+a.id+')">Del</button></div></td></tr>'
    ).join('')||'<tr><td colspan="7" class="empty">No appointments found</td></tr>';
    renderPagination('appts-pagination',apptPage,pages,p=>{apptPage=p;renderAppointments();},total);
}
function openAddApptModal(){
    document.getElementById('am-patient').innerHTML=allPatients.map(p=>'<option value="'+p.id+'">'+esc(p.name)+' (ID: '+p.id+')</option>').join('');
    document.getElementById('am-doctor').innerHTML=allDoctors.map(d=>'<option value="'+d.id+'">'+esc(d.name)+' — '+esc(d.department)+'</option>').join('');
    document.getElementById('am-datetime').value='';document.getElementById('am-reason').value='';
    document.getElementById('appt-modal-err').style.display='none';
    openModal('appt-modal');
}
async function saveAppointment(){
    const err=document.getElementById('appt-modal-err');err.style.display='none';
    const patient_id=parseInt(document.getElementById('am-patient').value);
    const doctor_id=parseInt(document.getElementById('am-doctor').value);
    const dt=document.getElementById('am-datetime').value;
    const reason=document.getElementById('am-reason').value.trim();
    if(!patient_id||!doctor_id||!dt){err.textContent='Patient, doctor, and date are required';err.style.display='block';return;}
    try{
        await apiPost('/appointments/',{patient_id,doctor_id,date_time:new Date(dt).toISOString(),reason});
        toast('Appointment created','success');
        closeModal('appt-modal');
        await loadAppointments();renderAppointments();loadOverview();
    }catch(e){err.textContent=e.message;err.style.display='block';}
}
function openStatusModal(id,current){
    document.getElementById('sm-id').value=id;
    document.getElementById('sm-status').value=current;
    openModal('status-modal');
}
async function changeApptStatus(){
    const id=document.getElementById('sm-id').value;
    const status=document.getElementById('sm-status').value;
    try{
        await apiPatch('/appointments/'+id,{status});
        toast('Status updated','success');closeModal('status-modal');
        await loadAppointments();renderAppointments();loadOverview();
    }catch(e){toast('Error: '+e.message,'error');}
}
function openRecordModal(apptId, patientId, doctorId){
    if (ROLE === 'receptionist') {
        toast('Only doctors and admins can create medical records', 'error');
        return;
    }
    selectedRecordApptId = apptId;
    selectedRecordPatientId = patientId;
    document.getElementById('record-modal-err').style.display='none';
    document.getElementById('record-modal-meta').textContent = 'Appointment #' + apptId + ' | Patient: ' + patientName(patientId) + ' | Doctor: ' + doctorName(doctorId);
    document.getElementById('rm-diagnosis').value='';
    document.getElementById('rm-prescription').value='';
    document.getElementById('rm-notes').value='';
    document.getElementById('rm-file').value='';
    openModal('record-modal');
}

async function saveMedicalRecordFromAppointment(){
    const err=document.getElementById('record-modal-err');
    err.style.display='none';
    const diagnosis=document.getElementById('rm-diagnosis').value.trim();
    const prescription=document.getElementById('rm-prescription').value.trim();
    const notes=document.getElementById('rm-notes').value.trim();
    const fileInput=document.getElementById('rm-file');
    if(!selectedRecordApptId){
        err.textContent='Appointment not selected';
        err.style.display='block';
        return;
    }
    if(!diagnosis){
        err.textContent='Diagnosis is required';
        err.style.display='block';
        return;
    }
    if(!fileInput.files || !fileInput.files[0]){
        err.textContent='Please select a file';
        err.style.display='block';
        return;
    }

    const form = new FormData();
    form.append('diagnosis', diagnosis);
    form.append('prescription', prescription);
    form.append('notes', notes);
    form.append('file', fileInput.files[0]);

    try{
        const r=await fetch(API+'/appointments/'+selectedRecordApptId+'/records',{
            method:'POST',
            headers:{'Authorization':'Bearer '+TOKEN},
            body:form,
        });
        if(!r.ok){
            const e=await r.json().catch(()=>({}));
            throw new Error(e.detail||r.statusText||'Failed to save medical record');
        }
        toast('Medical record added','success');
        closeModal('record-modal');

        // Refresh related datasets to show the new record immediately.
        await Promise.all([loadPatients(), loadDoctors(), loadAppointments()]);
        renderAppointments();
        if(selectedRecordPatientId){
            await showPatientDetail(selectedRecordPatientId);
        }
    }catch(e){
        err.textContent=e.message;
        err.style.display='block';
    }
}

async function deleteAppointment(id){
    if(!confirm('Delete this appointment?'))return;
    try{await apiDelete('/appointments/'+id);toast('Appointment deleted','success');await loadAppointments();renderAppointments();loadOverview();}
    catch(e){toast('Error: '+e.message,'error');}
}

/* ===== Pagination ===== */
function renderPagination(elId,current,total,onPage,count){
    const el=document.getElementById(elId);
    if(total<=1){el.innerHTML=count?'<span class="pg-info">'+count+' records</span>':'';return;}
    let h='<span class="pg-info">'+count+' records</span>';
    h+='<button class="pg-btn" id="'+elId+'-prev" '+(current<=1?'disabled':'')+'>&#171; Prev</button>';
    let s=Math.max(1,current-2),e=Math.min(total,s+4);if(e-s<4)s=Math.max(1,e-4);
    for(let i=s;i<=e;i++)h+='<button class="pg-btn '+(i===current?'active':'')+'" data-pg="'+i+'">'+i+'</button>';
    h+='<button class="pg-btn" id="'+elId+'-next" '+(current>=total?'disabled':'')+'>Next &#187;</button>';
    el.innerHTML=h;
    el.querySelector('#'+elId+'-prev').addEventListener('click',()=>{if(current>1)onPage(current-1);});
    el.querySelector('#'+elId+'-next').addEventListener('click',()=>{if(current<total)onPage(current+1);});
    el.querySelectorAll('[data-pg]').forEach(b=>b.addEventListener('click',()=>onPage(parseInt(b.dataset.pg))));
}

/* ===== Reset modal fields on open for "Add" ===== */
document.querySelector('#patient-modal .btn-success,button[onclick="openModal(\'patient-modal\')"]');
/* We handle resetting via the + Add buttons: */
document.querySelectorAll('button').forEach(b=>{
    if(b.textContent.includes('+ Add Patient'))b.addEventListener('click',()=>{
        document.getElementById('patient-modal-title').textContent='Add New Patient';
        document.getElementById('pm-id').value='';document.getElementById('pm-name').value='';
        document.getElementById('pm-age').value='';document.getElementById('pm-contact').value='';
        document.getElementById('pm-address').value='';document.getElementById('pm-blood').value='';
        document.getElementById('patient-modal-err').style.display='none';
    });
    if(b.textContent.includes('+ Add Doctor'))b.addEventListener('click',()=>{
        document.getElementById('doctor-modal-title').textContent='Add New Doctor';
        document.getElementById('dm-id').value='';document.getElementById('dm-name').value='';
        document.getElementById('dm-spec').value='';document.getElementById('dm-dept').value='';
        document.getElementById('dm-contact').value='';
        document.getElementById('doctor-modal-err').style.display='none';
    });
    if(b.textContent.includes('+ Add User'))b.addEventListener('click',()=>{
        document.getElementById('um-username').value='';document.getElementById('um-password').value='';
        document.getElementById('um-fullname').value='';
        document.getElementById('user-modal-err').style.display='none';
    });
});
window.addEventListener('DOMContentLoaded', () => {
    const savedToken = localStorage.getItem('hc_token');
    if (savedToken) {
        TOKEN = savedToken;
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('app').style.display = 'block';
        initApp();
    }
});
</script>
</body>
</html>
"""
