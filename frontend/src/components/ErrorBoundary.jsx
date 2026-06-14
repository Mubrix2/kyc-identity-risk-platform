// frontend/src/components/ErrorBoundary.jsx
import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { error: null } }
  static getDerivedStateFromError(error) { return { error } }

  render() {
    if (this.state.error) {
      return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="font-semibold text-red-700 mb-2">Error rendering case detail</h3>
            <p className="text-xs text-gray-500 font-mono mb-4">{this.state.error?.message}</p>
            <button onClick={() => { this.setState({ error: null }); this.props.onClose?.() }}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200">
              Close
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}