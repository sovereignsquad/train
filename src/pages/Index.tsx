
import RomaSlideshow from '@/components/RomaSlideshow';

const Index = () => {
  return (
    <div className="min-h-screen w-full relative overflow-hidden bg-roma-gradient bg-400% animate-gradient-shift">
      {/* Background overlay for better contrast */}
      <div className="absolute inset-0 bg-black/20"></div>
      
      {/* Main content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-4">
        {/* Title with semi-transparent background */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-20 pointer-events-none">
          <div className="bg-black/50 backdrop-blur-sm rounded-lg px-6 py-4 sm:px-8 sm:py-6 md:px-12 md:py-8 border border-roma-gold/30">
            <h1 className="text-3xl sm:text-4xl md:text-6xl lg:text-7xl xl:text-8xl font-bold text-white text-center animate-fade-in">
              <span className="bg-gradient-to-r from-roma-gold via-roma-orange to-roma-red bg-clip-text text-transparent">
                WE LOVE
              </span>
              <br />
              <span className="text-roma-red drop-shadow-lg">
                ROMA
              </span>
            </h1>
          </div>
        </div>
        
        {/* Slideshow container */}
        <div className="w-full h-full flex items-center justify-center">
          <div className="w-full max-w-7xl">
            <RomaSlideshow />
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-10 left-10 w-20 h-20 bg-roma-gold/20 rounded-full blur-xl animate-pulse"></div>
        <div className="absolute bottom-10 right-10 w-32 h-32 bg-roma-red/20 rounded-full blur-xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/4 right-20 w-16 h-16 bg-roma-orange/20 rounded-full blur-xl animate-pulse delay-500"></div>
      </div>
      
      {/* Bottom gradient overlay */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black/30 to-transparent pointer-events-none"></div>
    </div>
  );
};

export default Index;
