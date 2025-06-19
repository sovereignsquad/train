
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';

interface SlideshowImage {
  id: string;
  url: string;
  title?: string;
}

// Fallback Roma images (using placeholder service with Roma-themed URLs)
const fallbackImages: SlideshowImage[] = [
  {
    id: '1',
    url: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=700&fit=crop&crop=center',
    title: 'AS Roma Stadium'
  },
  {
    id: '2', 
    url: 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=400&h=700&fit=crop&crop=center',
    title: 'Roma Fans'
  },
  {
    id: '3',
    url: 'https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=400&h=700&fit=crop&crop=center',
    title: 'Football Stadium'
  },
  {
    id: '4',
    url: 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=400&h=700&fit=crop&crop=center',
    title: 'Roma Colors'
  },
  {
    id: '5',
    url: 'https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=400&h=700&fit=crop&crop=center',
    title: 'Football Action'
  },
  {
    id: '6',
    url: 'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=400&h=700&fit=crop&crop=center',
    title: 'Stadium Atmosphere'
  },
  {
    id: '7',
    url: 'https://images.unsplash.com/photo-1577223625816-7546f13df25d?w=400&h=700&fit=crop&crop=center',
    title: 'Football Glory'
  },
  {
    id: '8',
    url: 'https://images.unsplash.com/photo-1506629905814-b9b6096e9d5b?w=400&h=700&fit=crop&crop=center',
    title: 'Team Spirit'
  }
];

const fetchSlideshow = async (): Promise<SlideshowImage[]> => {
  console.log('Attempting to fetch slideshow from API...');
  
  try {
    const response = await fetch(
      'https://api.seyu.hu/seyu/backend/slideshow?event-id=1769&slideshow-id=2192&enable-poster=0&token=eyJhbGciOiJIUzI1NiJ9.eyJzbGlkZXNob3dJZCI6MjE5Mn0.GpxJfbgRUdkuI-NdT3e6qCQ7KNhdmq-MTvShHC5e-CU',
      {
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        }
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('API slideshow data:', data);
    
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
    
    // If we can't parse the response, use fallback
    console.log('Could not parse API response, using fallback images');
    return fallbackImages;
    
  } catch (error) {
    console.log('API fetch failed, using fallback images:', error);
    return fallbackImages;
  }
};

const RomaSlideshow = () => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  const { data: images = fallbackImages, isLoading, error } = useQuery({
    queryKey: ['slideshow'],
    queryFn: fetchSlideshow,
    refetchOnWindowFocus: false,
    retry: 1,
    // Use fallback images immediately if query fails
    placeholderData: fallbackImages
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

  // Always show images (either from API or fallback)
  const displayImages = images.length > 0 ? images : fallbackImages;
  const gridImages = displayImages.slice(0, 8);
  
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
                  // Don't hide the image, let browser show broken image icon
                }}
                loading="lazy"
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
        
        {/* Status indicator */}
        {error && (
          <div className="text-center mt-2">
            <p className="text-xs text-white/60">Using demo images (API unavailable)</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RomaSlideshow;
