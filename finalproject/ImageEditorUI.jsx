import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Upload } from "lucide-react";
import { motion } from "framer-motion";

export default function ImageEditorUI() {
  const [image, setImage] = useState(null);
  const [sliders, setSliders] = useState({
    blur: 0,
    grayscale: 0,
    brightness: 100,
    contrast: 100,
    edge: 0,
  });

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(URL.createObjectURL(file));
    }
  };

  const updateSlider = (key, value) => {
    setSliders({ ...sliders, [key]: value[0] });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold mb-6 text-center"
        >
          Image Editor
        </motion.h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Upload + Preview */}
          <Card className="col-span-2 bg-gray-800 border-none shadow-xl rounded-2xl">
            <CardContent className="p-6 flex flex-col items-center justify-center h-full">
              {!image ? (
                <label className="cursor-pointer flex flex-col items-center gap-4">
                  <Upload size={40} />
                  <span className="text-gray-300">Upload an image</span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                </label>
              ) : (
                <img
                  src={image}
                  alt="Preview"
                  className="rounded-xl max-h-[500px] object-contain shadow-lg"
                />
              )}
            </CardContent>
          </Card>

          {/* Controls */}
          <Card className="bg-gray-800 border-none shadow-xl rounded-2xl">
            <CardContent className="p-6 space-y-6">
              {Object.entries(sliders).map(([key, value]) => (
                <div key={key}>
                  <div className="flex justify-between mb-2 capitalize">
                    <span>{key}</span>
                    <span className="text-gray-400">{value}</span>
                  </div>
                  <Slider
                    defaultValue={[value]}
                    max={key === "brightness" || key === "contrast" ? 200 : 100}
                    step={1}
                    onValueChange={(val) => updateSlider(key, val)}
                  />
                </div>
              ))}

              <Button className="w-full mt-4 bg-blue-600 hover:bg-blue-700 rounded-xl">
                Apply Filters
              </Button>

              <Button variant="outline" className="w-full rounded-xl">
                Reset
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
