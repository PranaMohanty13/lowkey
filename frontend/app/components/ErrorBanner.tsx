type ErrorBannerProps = {
  message: string;
};

export function ErrorBanner({ message }: ErrorBannerProps) {
  return (
    <div className="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
      Error: {message}
    </div>
  );
}
