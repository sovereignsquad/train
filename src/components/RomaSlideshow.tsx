
const RomaSlideshow = () => {
  const slideshowUrl = 'https://api.seyu.hu/seyu/backend/slideshow?event-id=1769&slideshow-id=2192&enable-poster=0&token=eyJhbGciOiJIUzI1NiJ9.eyJzbGlkZXNob3dJZCI6MjE5Mn0.GpxJfbgRUdkuI-NdT3e6qCQ7KNhdmq-MTvShHC5e-CU';

  return (
    <div className="w-full h-full flex items-center justify-center p-4">
      <div className="relative max-w-6xl w-full">
        <div className="aspect-[16/18] w-full max-h-[85vh]">
          <iframe
            src={slideshowUrl}
            className="w-full h-full rounded-md border-2 border-roma-gold/30"
            title="Roma Slideshow"
            allowFullScreen
            style={{
              border: 'none',
              borderRadius: '8px'
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default RomaSlideshow;
