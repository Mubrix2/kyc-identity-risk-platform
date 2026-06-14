// frontend/src/components/SubmitForm.jsx
import { useState } from 'react'
import { submitApplication } from '../api/client'

// Presets demonstrate each decision path — same idea as Project 1's
// suspicious/legitimate buttons.
const PRESETS = {
  clean: {
    label: '✅ Clean Application',
    image: '/sample_ids/clean_match.png',
    fields: {
      declared_name: 'ADEKUNLE OKAFOR', declared_dob: '14/03/1990',
      declared_id_number: '12345678901', declared_id_type: 'NIN',
      email_domain_age_days: 800, phone_country_mismatch: false,
      ip_country_mismatch: false, device_fingerprint: 'device-clean-001',
    },
  },
  sanctions: {
    label: '⛔ Sanctions Match',
    image: '/sample_ids/clean_match.png',
    fields: {
      declared_name: 'ABBAS, ABU', declared_dob: '01/01/1980',
      declared_id_number: '99988877766', declared_id_type: 'PASSPORT',
      email_domain_age_days: 10, phone_country_mismatch: true,
      ip_country_mismatch: true, device_fingerprint: 'device-sanctions-002',
    },
  },
  pep: {
    label: '🔍 PEP Match',
    image: '/sample_ids/clean_match.png',
    fields: {
      declared_name: 'ADEBAYO JOHNSON', declared_dob: '20/05/1975',
      declared_id_number: '11122233344', declared_id_type: 'NIN',
      email_domain_age_days: 1200, phone_country_mismatch: false,
      ip_country_mismatch: false, device_fingerprint: 'device-pep-003',
    },
  },
  mismatch: {
    label: '⚠️ Document Mismatch',
    image: '/sample_ids/mismatch_name.png',  // declared name won't match this image
    fields: {
      declared_name: 'BENJAMIN ADEWALE', declared_dob: '22/07/1988',
      declared_id_number: '98765432109', declared_id_type: 'DRIVERS_LICENSE',
      email_domain_age_days: 5, phone_country_mismatch: false,
      ip_country_mismatch: false, device_fingerprint: 'device-mismatch-004',
    },
  },
}

const ID_TYPES = ['NIN', 'BVN', 'VOTERS_CARD', 'DRIVERS_LICENSE', 'PASSPORT']

export default function SubmitForm({ onSubmitted }) {
  const [fields, setFields] = useState(PRESETS.clean.fields)
  const [imagePath, setImagePath] = useState(PRESETS.clean.image)
  const [imageFile, setImageFile] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const set = (k, v) => setFields(f => ({ ...f, [k]: v }))

  const loadPreset = async (key) => {
    const preset = PRESETS[key]
    setFields({ ...preset.fields, device_fingerprint: `${preset.fields.device_fingerprint}-${Date.now()}` })
    setImagePath(preset.image)
    setImageFile(null)  // will fetch the sample image at submit time
    setResult(null)
    setError(null)
  }

  const submit = async () => {
    setSubmitting(true)
    setError(null)
    try {
      const formData = new FormData()
      Object.entries(fields).forEach(([k, v]) => formData.append(k, v))

      let fileBlob = imageFile
      if (!fileBlob) {
        const imgResp = await fetch(imagePath)
        fileBlob = await imgResp.blob()
      }
      formData.append('document', fileBlob, 'id.png')

      const resp = await submitApplication(formData)
      setResult(resp)
      onSubmitted?.()
    } catch (e) {
      setError(e.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
      <h2 className="font-semibold text-gray-800 mb-3">New KYC Application</h2>

      <div className="flex gap-2 mb-4 flex-wrap">
        {Object.entries(PRESETS).map(([key, p]) => (
          <button key={key} onClick={() => loadPreset(key)}
            className="px-3 py-1 text-xs bg-gray-50 border border-gray-200 rounded hover:bg-gray-100">
            {p.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
        <div>
          <label className="text-xs text-gray-500 mb-0.5 block">Declared Name</label>
          <input value={fields.declared_name} onChange={e => set('declared_name', e.target.value)}
            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-0.5 block">DOB (DD/MM/YYYY)</label>
          <input value={fields.declared_dob} onChange={e => set('declared_dob', e.target.value)}
            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-0.5 block">ID Number</label>
          <input value={fields.declared_id_number} onChange={e => set('declared_id_number', e.target.value)}
            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-0.5 block">ID Type</label>
          <select value={fields.declared_id_type} onChange={e => set('declared_id_type', e.target.value)}
            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5">
            {ID_TYPES.map(t => <option key={t}>{t}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-0.5 block">Email Domain Age (days)</label>
          <input type="number" value={fields.email_domain_age_days}
            onChange={e => set('email_domain_age_days', parseInt(e.target.value) || 0)}
            className="w-full text-sm border border-gray-200 rounded px-2 py-1.5" />
        </div>
        <div className="flex items-center gap-2 mt-5">
          <input type="checkbox" checked={fields.phone_country_mismatch}
            onChange={e => set('phone_country_mismatch', e.target.checked)} />
          <label className="text-xs text-gray-600">Phone/IP country mismatch</label>
          <input type="checkbox" checked={fields.ip_country_mismatch}
            onChange={e => set('ip_country_mismatch', e.target.checked)} className="ml-2" />
        </div>
        <div className="md:col-span-2">
          <label className="text-xs text-gray-500 mb-0.5 block">ID Document Image</label>
          <input type="file" accept="image/*"
            onChange={e => { setImageFile(e.target.files[0]); setImagePath(null) }}
            className="w-full text-xs" />
          {imagePath && !imageFile && (
            <p className="text-xs text-gray-400 mt-1">Using preset image: {imagePath.split('/').pop()}</p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button onClick={submit} disabled={submitting}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 disabled:opacity-50">
          {submitting ? 'Processing...' : 'Submit Application'}
        </button>
        {result && (
          <span className="text-xs text-gray-600">
            ✓ {result.record_id} → <strong>{result.decision}</strong> ({(result.risk_probability * 100).toFixed(1)}%)
          </span>
        )}
        {error && <span className="text-xs text-red-600">Error: {error}</span>}
      </div>
    </div>
  )
}