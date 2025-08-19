import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../api/axios'


export default function WorkFlowView() {
const { id } = useParams()
const [workflow, setWorkflow] = useState(null)
const [loading, setLoading] = useState(true)


useEffect(()=>{
    let mounted = true
    api.get(`/workflows/${id}`).then(res=>{
        if(!mounted) return
        setWorkflow(res.data)
    }).catch(err=>console.error(err)).finally(()=> mounted && setLoading(false))
    return ()=> { mounted = false }
},[id])


if (loading) return <div className="p-6">Loading...</div>
if (!workflow) return <div className="p-6">Workflow not found</div>


return (
<div className="p-6">
<h2 className="text-xl font-bold mb-2">{workflow.name}</h2>
<pre className="bg-gray-100 p-4 rounded">{workflow.definition}</pre>
</div>
)
}