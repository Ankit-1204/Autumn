import React, { useState } from 'react'
import api from '../api/axios'


export default function RunButton({ workflowId, onOpenLog }) {
const [running, setRunning] = useState(false)


async function startRun() {
    setRunning(true)
    try {
        const res = await api.post(`/workflows/${workflowId}/runs`)
        const run = res.data
        const token = localStorage.getItem('token')

        const httpBase = import.meta.env.VITE_WS_URL || import.meta.env.VITE_API_URL || window.location.origin
        const wsBase = httpBase.replace(/^http/, 'ws').replace(/\/$/, '')
        const ws = new WebSocket(`${wsBase}/ws/runs/${run.id}?token=${encodeURIComponent(token)}`)

        let combined = ''
        ws.onmessage = (ev) => {
            try {
                const data = JSON.parse(ev.data)
                if (data.type && data.type.startsWith('step')) {
                    combined += (data.step_instance?.logs || JSON.stringify(data)) + '\n'
                } else if (data.type === 'run.started') {
                    combined += 'Run started\n'
                } else if (data.type === 'run.finished') {
                    combined += 'Run finished\n'
                    ws.close()
                }
                onOpenLog(combined)
            } catch (e) {
                console.warn('ws parsing', e)
            }
        }
        ws.onclose = () => setRunning(false)
    } catch (err) {
        console.error(err)
        alert('Failed to start run')
        setRunning(false)
    }
}


return (
<button onClick={startRun} disabled={running} className="px-3 py-1 bg-blue-600 text-white rounded text-sm">
{running ? 'Running...' : 'Run'}
</button>
)
}