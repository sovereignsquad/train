
const RomaSlideshow = () => {
  const slideshowUrl = 'https://api.seyu.hu/seyu/backend/slideshow?event-id=1769&slideshow-id=2192&enable-poster=0&token=eyJhbGciOiJIUzI1NiJ9.eyJzbGlkZXNob3dJZCI6MjE5Mn0.GpxJfbgRUdkuI-NdT3e6qCQ7KNhdmq-MTvShHC5e-CU';

  return (
    <div className="w-full h-full flex items-center justify-center p-4">
      <div className="relative max-w-6xl w-full">
        <div style={{ aspectRatio: '9 / 8', width: '100%', maxWidth: '100vw' }}>
          <iframe
            src={slideshowUrl}
            style={{ width: '100%', height: '100%', border: 'none' }}
            className="rounded-md border-2 border-roma-gold/30"
            title="Roma Slideshow"
            allowFullScreen
          />
        </div>
      </div>
    </div>
  );
};

export default RomaSlideshow;
