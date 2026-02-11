export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-8" role="status" aria-live="polite">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
      <span className="sr-only">Loading</span>
    </div>
  );
}

export function ErrorMessage({ message, onDismiss }) {
  return (
    <div 
      className="bg-red-900/30 border border-red-500/50 rounded-lg p-4 mb-4"
      role="alert"
      aria-live="assertive"
    >
      <div className="flex justify-between items-start gap-4">
        <div className="text-red-300 flex-1">
          <p className="font-semibold mb-1">⚠️ Error</p>
          <p className="text-sm">{message}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-red-400 hover:text-red-300 text-lg flex-shrink-0 p-1"
            aria-label="Dismiss error message"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}

export function SuccessMessage({ message, onDismiss }) {
  return (
    <div 
      className="bg-green-900/30 border border-green-500/50 rounded-lg p-4 mb-4"
      role="status"
      aria-live="polite"
    >
      <div className="flex justify-between items-start gap-4">
        <div className="text-green-300 flex-1">
          <p className="font-semibold mb-1">✓ Success</p>
          <p className="text-sm">{message}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-green-400 hover:text-green-300 text-lg flex-shrink-0 p-1"
            aria-label="Dismiss success message"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}

export function InfoMessage({ message }) {
  return (
    <div 
      className="bg-blue-900/30 border border-blue-500/50 rounded-lg p-4 mb-4"
      role="status"
      aria-live="polite"
    >
      <div className="text-blue-300">
        <p className="text-sm">ℹ️ {message}</p>
      </div>
    </div>
  );
}
