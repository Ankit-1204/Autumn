import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'
import RunButton from '../components/RunButton'


export default function Dashboard() {
const [workflows, setWorkflows] = useState([])
const [loading, setLoading] = useState(true)
const [selectedRunLog, setSelectedRunLog] = useState(null)


useEffect(() => {
let mounted = true
async function load() {
try {
const res = await api.get('/workflows')
if (mounted) setWorkflows(res.data || [])
} catch (err) {
console.error(err)
alert('Failed to fetch workflows')
} finally { if (mounted) setLoading(false) }
}
load()
return () => { mounted = false }
}, [])


if (loading) return <div className="p-6">Loading...</div>


return (
<div className="p-6">
<h1 className="text-2xl font-bold mb-4">Your workflows</h1>
<div className="space-y-4">
{workflows.length === 0 && <div className="text-gray-600">You have no workflows yet.</div>}
{workflows.map(wf => (
<div key={wf.id} className="border rounded p-4 flex justify-between items-center">
<div>
<div className="font-semibold">{wf.name}</div>
<div className="text-sm text-gray-500">Created: {new Date(wf.created_at).toLocaleString()}</div>
</div>
<div className="flex gap-2">
<RunButton workflowId={wf.id} onOpenLog={(log)=>setSelectedRunLog(log)} />
<Link to={`/workflows/${wf.id}`} className="px-3 py-1 border rounded text-sm">Open</Link>
</div>
</div>
))}
</div>


{selectedRunLog && (
<div className="mt-6 bg-gray-800 text-white p-4 rounded">
<h3 className="font-bold mb-2">Run logs</h3>
<pre className="whitespace-pre-wrap">{selectedRunLog}</pre>
<button onClick={()=>setSelectedRunLog(null)} className="mt-2 px-3 py-1 bg-gray-200 text-black rounded">Close</button>
</div>
)}
</div>)
}