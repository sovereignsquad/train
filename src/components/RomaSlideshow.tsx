
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';

interface SlideshowImage {
  id: string;
  url: string;
  title?: string;
}

const fetchSlideshow = async (): Promise<SlideshowImage[]> => {
  const response = await fetch(
    'https://api.seyu.hu/seyu/backend/slideshow?event-id=1769&slideshow-id=2192&enable-poster=0&token=eyJhbGciOiJIUzI1NiJ9.eyJzbGlkZXNob3dJZCI6MjE5Mn0.GpxJfbgRUdkuI-NdT3e6qCQ7KNhdmq-MTvShHC5e-CU'
  );
  
  if (!response.ok) {
    throw new Error('Failed to fetch slideshow');
  }
  
  const data = await response.json();
  console.log('Slideshow data:', data);
  
  // Transform the API response to our expected format
  if (data.images && Array.isArray(data.images)) {
    return data.images.map((img: any, index: number) => ({
      id: img.id || index.toString(),
      url: img.url || img.src || img.image,
      title: img.title || img.name
    }));
  }
  
  // If the response structure is different, try to extract images
  if (Array.isArray(data)) {
    return data.map((img: any, index: number) => ({
      id: img.id || index.toString(),
      url: img.url || img.src || img.image || img,
      title: img.title || img.name
    }));
  }
  
  // Fallback: return empty array if we can't parse the response
  return [];
};

const RomaSlideshow = () => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  const { data: images = [], isLoading, error } = useQuery({
    queryKey: ['slideshow'],
    queryFn: fetchSlideshow,
    refetchOnWindowFocus: false,
    retry: 2
  });

  useEffect(() => {
    if (images.length > 0) {
      const interval = setInterval(() => {
        setCurrentImageIndex((prev) => (prev + 1) % images.length);
      }, 4000);
      return () => clearInterval(interval);
    }
  }, [images.length]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center w-full h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-roma-gold border-t-transparent"></div>
      </div>
    );
  }

  if (error) {
    console.error('Slideshow error:', error);
    return (
      <div className="text-center text-white/80">
        <p>Unable to load slideshow</p>
        <p className="text-sm mt-2">Check console for details</p>
      </div>
    );
  }

  if (images.length === 0) {
    return (
      <div className="text-center text-white/80">
        <p>No images available</p>
      </div>
    );
  }

  // Create a 4x2 grid with the first 8 images
  const gridImages = images.slice(0, 8);
  
  return (
    <div className="w-full h-full flex items-center justify-center p-4">
      <div className="relative max-w-6xl w-full">
        {/* 4x2 Grid Layout */}
        <div className="grid grid-cols-4 grid-rows-2 gap-1 sm:gap-2 md:gap-3 aspect-[16/18] w-full max-h-[85vh]">
          {gridImages.map((image, index) => (
            <div 
              key={image.id} 
              className={`relative overflow-hidden rounded-sm sm:rounded-md transition-all duration-500 ${
                index === currentImageIndex ? 'ring-2 ring-roma-gold shadow-lg shadow-roma-gold/20' : ''
              }`}
            >
              <img
                src={image.url}
                alt={image.title || `Roma image ${index + 1}`}
                className="w-full h-full object-cover transition-transform duration-700 hover:scale-105"
                onError={(e) => {
                  console.error(`Failed to load image ${index}:`, image.url);
                  e.currentTarget.style.display = 'none';
                }}
              />
              {/* Subtle overlay for active image */}
              {index === currentImageIndex && (
                <div className="absolute inset-0 bg-roma-gold/10 pointer-events-none"></div>
              )}
            </div>
          ))}
        </div>
        
        {/* Navigation dots */}
        <div className="flex justify-center mt-4 space-x-2">
          {gridImages.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentImageIndex(index)}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                index === currentImageIndex 
                  ? 'bg-roma-gold scale-125' 
                  : 'bg-white/40 hover:bg-white/60'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default RomaSlideshow;
