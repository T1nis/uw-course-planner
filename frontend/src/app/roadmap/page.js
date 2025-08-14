// Marks this as a client-side component in Next.js (runs in browser, not server)
"use client";

// Import React and useState hook for managing component state
import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

// Import various icon components from Lucide React icon library
import { Search, Plus, Check, Clock, Star, TrendingUp, BookOpen, Users, Calendar, ChevronDown, ChevronUp, ChevronLeft, ChevronRight } from 'lucide-react';
// Import custom Navigation component from separate file
import Navigation from './NavBar';

// Mock data for completed courses - organized by semester
// Each course object contains: code, name, credits, grade, semester, requirement type
// With this:


// Mock course database for search functionality
// Contains available courses with detailed information including:
// - Basic info (code, name, credits, requirement)
// - Course description
// - MadGrades data (GPA and difficulty ratings)
// - Rate My Professor data (rating and top professor)
// - Prerequisites list
 // Replace hardcoded courseDatabase with fetched data




// Main component definition
export default function RoadmapPage() {

  const [completedCourses, setCompletedCourses] = useState({
  "Fall 2024": [],
  "Spring 2024": []
});

    const [courseDatabase, setCourseDatabase] = useState([]);
useEffect(() => {
  fetch('http://127.0.0.1:5000/api/courses')
    .then(res => res.json())
    .then(data => {
      // Map backend data to expected frontend format
      const mappedCourses = data.map(raw => ({
        code: raw.course_reference
          ? `${raw.course_reference.subjects[0]} ${raw.course_reference.course_number}`
          : '',

        name: raw.course_title || '',

        description: raw.description || '',

        credits: raw.cumulative_grade_data?.credit || 3, // fallback to 3 if not present

        requirement: '', // You can add logic to set this if you want

        prerequisites: raw.prerequisites?.course_references
          ? raw.prerequisites.course_references.map(pr => 
              pr.subjects ? `${pr.subjects[0]} ${pr.course_number}` : ''
            )
          : [],

        madGrades: {
          avgGPA: null, // Fill with your logic if you want
          difficulty: null // Fill with your logic if you want
        },

        rmp: {
          rating: null,
          professor: null
        }
      }));
      setCourseDatabase(mappedCourses);
    });
}, []);

  // State variables using useState hook
  const [searchTerm, setSearchTerm] = useState(''); // Stores the search input text
  const [selectedCourse, setSelectedCourse] = useState(null); // Stores currently selected course for modal
  const [showCourseSearch, setShowCourseSearch] = useState(false); // Controls visibility of course search panel
  const [showSemesterModal, setShowSemesterModal] = useState(false); // Controls visibility of semester selection modal
  const [courseToAdd, setCourseToAdd] = useState(null); // Stores course that user wants to add to roadmap
  const [semesterIndex, setSemesterIndex] = useState(0);
  
  // State for planned courses - organized by semester
  // This is where future courses are stored before they're taken
  const [plannedCourses, setPlannedCourses] = useState({
    "Fall 2025": [
      { code: 'CS 354', name: 'Machine Organization and Programming', credits: 3, requirement: 'Major Core' },
      { code: 'CS 577', name: 'Introduction to Algorithms', credits: 3, requirement: 'Major Core' },
      { code: 'STAT 324', name: 'Introductory Applied Statistics', credits: 3, requirement: 'Major Requirement' }
    ],
    "Spring 2026": [], // Empty array means no courses planned for this semester
    "Fall 2026": [], 
    "Fall 2027": [
      { code: 'CS 600', name: 'Capstone Project', credits: 3, requirement: 'Major Core' }
    ],
    "Spring 2027": [
      { code: 'CS 610', name: 'Advanced Topics in Computer Science', credits: 3, requirement: 'Major Elective' },
      { code: 'CS 620', name: 'Distributed Systems', credits: 3, requirement: 'Major Elective' }
    ],
    "Spring 2028": [],
  });

  // Calculate progress statistics
  // Flatten all completed courses and sum their credits
  const totalCreditsCompleted = Object.values(completedCourses)
  .flat()
  .reduce((sum, course) => sum + course.credits, 0);
  
  // Flatten all planned courses and sum their credits
  const totalCreditsPlanned = Object.values(plannedCourses)
  .flat()
  .reduce((sum, course) => sum + course.credits, 0);
  
  const totalCreditsNeeded = 120; // Typical CS degree requirement
  
  // Calculate completion percentage (completed credits / total needed)
  const progressPercentage = Math.round((totalCreditsCompleted / totalCreditsNeeded) * 100);
  
  // Calculate projected percentage including planned courses
  const plannedProgressPercentage = Math.round(((totalCreditsCompleted + totalCreditsPlanned) / totalCreditsNeeded) * 100);
const majorRequirements = [
  'CS 300',
  'CS 301',
  'CS 302',
  'CS 400',
  'CS 540',
  'MATH 234',
  'STAT 324'
];


const filteredCourses = courseDatabase.filter(course =>
  course.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
  course.name.toLowerCase().includes(searchTerm.toLowerCase())
);

// ✅ FIRST: define the function
const getPriorityCourses = (completed, planned, requirements, database) => {
  const completedCodes = completed.flat().map(c => c.code);
  const plannedCodes = planned.flat().map(c => c.code);
  const taken = new Set([...completedCodes, ...plannedCodes]);

  const remaining = requirements.filter(code => !taken.has(code));

  const priorityCourses = remaining.map(code => {
    const dependents = database.filter(c => 
      requirements.includes(c.code) && 
      c.prerequisites?.includes(code)
    ).length;

    const courseObj = database.find(c => c.code === code);
    if (!courseObj) console.warn("Missing course in courseDatabase:", code);

    return {
      code,
      dependentCount: dependents,
      course: courseObj
    };
  });

  return priorityCourses
    .sort((a, b) => b.dependentCount - a.dependentCount)
    .filter(p => p.course)
    .map(p => p.course)
    .slice(0, 3);
};

// ✅ THEN: use it
const priorityCourses = getPriorityCourses(
  Object.values(completedCourses).flat(),
  Object.values(plannedCourses).flat(),
  majorRequirements,
  courseDatabase
);


  // CourseCard component - displays individual course information
  // Takes course object and status ('completed', 'planned', or 'available')
  const CourseCard = ({ course, status = 'available' }) => (
    <div 
      className={`p-4 rounded-xl border transition-all cursor-pointer ${
        status === 'completed' 
          ? 'bg-green-500/10 border-green-400/30 hover:bg-green-500/20' // Green styling for completed courses
          : status === 'planned'
          ? 'bg-blue-500/10 border-blue-400/30 hover:bg-blue-500/20' // Blue styling for planned courses
          : 'bg-white/5 border-white/20 hover:bg-white/10 hover:border-white/30' // Default styling for available courses
      }`}
      onClick={() => setSelectedCourse(course)} // Open course details modal when clicked
    >
      <div className="flex justify-between items-start mb-2">
        <div>
          <h4 className="font-semibold text-white">{course.code}</h4>
          <p className="text-sm text-gray-300">{course.name}</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Show different icons based on course status */}
          {status === 'completed' && <Check className="w-4 h-4 text-green-400" />}
          {status === 'planned' && <Clock className="w-4 h-4 text-blue-400" />}
          {/* Credits badge */}
         <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded-full whitespace-nowrap">
  {course.credits} cr
</span>
        </div>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400">{course.requirement}</span>
        {/* Show grade for completed courses */}
        {status === 'completed' && course.grade && (
          <span className="text-xs font-medium text-green-300">{course.grade}</span>
        )}
        {/* Show semester for planned courses */}
        {status === 'planned' && course.semester && (
          <span className="text-xs text-blue-300">{course.semester}</span>
        )}
      </div>
    </div>
  );

    

 const SemesterModal = ({ course, plannedCourses, completedCourses, onClose, onAdd }) => {
  const [addType, setAddType] = useState('planned'); // 'planned' or 'completed'
  if (!course) return null;

  // Use the correct semesters based on addType
  const availableSemesters = addType === 'planned'
    ? Object.keys(plannedCourses)
    : Object.keys(completedCourses);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div className="bg-[#1a1b2e] border border-white/20 rounded-2xl p-6 max-w-md w-full" onClick={e => e.stopPropagation()}>
        <h3 className="text-xl font-bold text-white mb-4">Add {course.code} to Roadmap</h3>
        <div className="flex gap-2 mb-6">
          <button
            type="button"
            className={`flex-1 py-2 rounded-xl ${addType === 'planned' ? 'bg-blue-500 text-white' : 'bg-gray-700 text-gray-300'}`}
            onClick={() => setAddType('planned')}
          >
            Planned
          </button>
          <button
            type="button"
            className={`flex-1 py-2 rounded-xl ${addType === 'completed' ? 'bg-green-500 text-white' : 'bg-gray-700 text-gray-300'}`}
            onClick={() => setAddType('completed')}
          >
            Completed
          </button>
        </div>
        <div className="space-y-3 mb-6">
          {availableSemesters.map(semester => (
            <button
              key={semester}
              type="button"
              onClick={() => onAdd(semester, addType)}
              className="w-full text-left p-4 bg-white/5 hover:bg-white/10 border border-white/20 rounded-xl transition"
            >
              <div className="text-white font-medium">{semester}</div>
              <div className="text-sm text-gray-400">
                {addType === 'planned'
                  ? plannedCourses[semester].length + ' courses currently planned'
                  : (completedCourses[semester]?.length || 0) + ' courses completed'}
              </div>
            </button>
          ))}
        </div>
        <button 
          type="button"
          onClick={onClose}
          className="w-full bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-xl transition"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};
 // CourseModal component - displays detailed course information
 const CourseModal = ({ course, onClose }) => {
  // Don't render if no course is selected
  if (!course) return null;
  
  // Function to handle adding course to roadmap
  const handleAddToRoadmap = () => {
    setCourseToAdd(course); // Set the course to be added
    setShowSemesterModal(true); // Show semester selection modal
    onClose(); // Close the course detail modal
  };

  // Function to remove course from planned courses
  const handleRemoveCourse = (courseToRemove) => {
  setPlannedCourses(prev => {
    const updated = {};

    // Loop through each semester and filter out the course to remove
    for (const semester in prev) {
      updated[semester] = prev[semester].filter(course => course.code !== courseToRemove.code);
    }

    return updated;
  });
};

  // Check if course is already planned
  const isCoursePlanned = Object.values(plannedCourses)
  .flat()
  .some(c => c.code === course.code);

    return (
      // Modal overlay
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" onClick={onClose}>
        {/* Modal content with scrollable area */}
        <div className="bg-[#1a1b2e] border border-white/20 rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
          {/* Modal header with close button */}
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-2xl font-bold text-white">{course.code}</h3>
              <p className="text-lg text-gray-300">{course.name}</p>
            </div>
          <button 
  onClick={onClose}
  className="text-gray-400 hover:text-white transition text-[40px] leading-none font-light px-2"
>
  ×
</button>

          </div>
          
          <div className="space-y-4">
            {/* Course description */}
            <div>
              <h4 className="font-semibold text-white mb-2">Description</h4>
              <p className="text-gray-300">{course.description}</p>
            </div>
            
            {/* Course statistics grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* MadGrades statistics */}
              <div className="bg-purple-500/10 border border-purple-400/30 rounded-xl p-4">
                <h5 className="font-semibold text-purple-300 mb-2 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  MadGrades Stats
                </h5>
                <p className="text-sm text-gray-300">Avg GPA: <span className="text-white font-medium">{course.madGrades?.avgGPA}</span></p>
                <p className="text-sm text-gray-300">Difficulty: <span className="text-white font-medium">{course.madGrades?.difficulty}/10</span></p>
              </div>
              
              {/* Rate My Professor statistics */}
              <div className="bg-orange-500/10 border border-orange-400/30 rounded-xl p-4">
                <h5 className="font-semibold text-orange-300 mb-2 flex items-center gap-2">
                  <Star className="w-4 h-4" />
                  Rate My Professor
                </h5>
                <p className="text-sm text-gray-300">Rating: <span className="text-white font-medium">{course.rmp?.rating}/5</span></p>
                <p className="text-sm text-gray-300">Top Prof: <span className="text-white font-medium">{course.rmp?.professor}</span></p>
              </div>
            </div>
            
            {/* Prerequisites section */}
            <div>
              <h5 className="font-semibold text-white mb-2">Prerequisites</h5>
              <div className="flex flex-wrap gap-2">
                {course.prerequisites?.map(prereq => (
                  <span key={prereq} className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full text-sm">
                    {prereq}
                  </span>
                ))}
              </div>
            </div>
            
            {/* Action button - either Add or Remove based on course status */}
            {isCoursePlanned ? (
  <button
    onClick={() => {
      handleRemoveCourse(course);
      onClose();
    }}
    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-3 rounded-xl transition"
  >
    Remove from Roadmap
  </button>
) : (
  <button
    onClick={handleAddToRoadmap}
    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-3 rounded-xl transition"
  >
    Add to Roadmap
  </button>
)}

          </div>
        </div>
      </div>
    );
  };

  // Function to handle adding course to selected semester
const handleAddCourse = (semester, addType) => {
  if (!courseToAdd) return;
  if (addType === 'planned') {
    setPlannedCourses(prev => ({
      ...prev,
      [semester]: [...prev[semester], { ...courseToAdd, semester }]
    }));
  } else {
    setCompletedCourses(prev => ({
      ...prev,
      [semester]: [...(prev[semester] || []), { ...courseToAdd, semester, grade: 'A' }] // You can prompt for grade if you want
    }));
  }
  setShowSemesterModal(false);
  setCourseToAdd(null);
};
  // Main component render
  return (

     <div>
      {/* Navigation component */}
      <Navigation /> 
      {/* Add padding-top to account for fixed navigation */}
      <div className="pt-16">

    {/* Main container with gradient background */}
    <div className="min-h-screen bg-gradient-to-br from-[#171923] via-[#22223c] to-[#29304d] p-4">
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-2">
            Computer Science Degree Roadmap
          </h1>
          <p className="text-gray-300">Track your progress and plan your path to graduation</p>
        </div>

        {/* Progress Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Overall Progress Card */}
          <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-lg">
            <div className="flex items-center gap-3 mb-4">
              <BookOpen className="w-6 h-6 text-blue-400" />
              <h3 className="text-lg font-semibold text-white">Overall Progress</h3>
            </div>
            <div className="space-y-3">
              {/* Completed progress */}
              <div className="flex justify-between text-sm">
                <span className="text-gray-300">Completed</span>
                <span className="text-white font-medium">{progressPercentage}%</span>
              </div>
              {/* Progress bar for completed courses */}
              <div className="w-full bg-gray-700 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-green-500 to-blue-500 h-3 rounded-full transition-all duration-1000"
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
              {/* Progress including planned courses */}
              <div className="flex justify-between text-sm">
                <span className="text-gray-300">With Planned</span>
                <span className="text-blue-300 font-medium">{plannedProgressPercentage}%</span>
              </div>
              {/* Progress bar including planned courses */}
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-green-500 via-blue-500 to-purple-500 h-2 rounded-full transition-all duration-1000"
                  style={{ width: `${plannedProgressPercentage}%` }}
                ></div>
              </div>
            </div>
          </div>
{/* Suggested Priority Courses Panel */}
<div className="bg-yellow-500/10 border border-yellow-400/20 rounded-2xl p-6 backdrop-blur-lg">
  <div className="flex items-center gap-3 mb-4">
    <TrendingUp className="w-6 h-6 text-yellow-300" />
    <h3 className="text-lg font-semibold text-white">Suggested for Next Semester</h3>
  </div>

  {priorityCourses.length === 0 ? (
    <p className="text-gray-300">You are all caught up on required courses!</p>
  ) : (
    <div className="space-y-4">
      {priorityCourses.map(course => (
        <div key={course.code} className="p-4 bg-white/5 border border-white/10 rounded-xl">
          <h4 className="text-white font-medium">{course.code} - {course.name}</h4>
          <p className="text-sm text-gray-300">{course.description}</p>
        </div>
      ))}
    </div>
  )}
</div>

          {/* Graduation Timeline Card */}
          <div className="bg-white/10 border border-white/20 rounded-2xl p-6 backdrop-blur-lg">
            <div className="flex items-center gap-3 mb-4">
              <Calendar className="w-6 h-6 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Graduation</h3>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                Spring 2026
              </div>
              <p className="text-sm text-gray-300 mt-1">Projected graduation</p>
              <div className="mt-3 text-xs text-green-300">
                ✓ On track
              </div>
            </div>
          </div>
        </div>

        {/* Course Search Toggle Button */}
        <div className="mb-6">
          <button
            onClick={() => setShowCourseSearch(!showCourseSearch)} // Toggle search panel visibility
            className="flex items-center gap-2 bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-400/30 rounded-xl px-6 py-3 text-white hover:from-blue-500/30 hover:to-purple-500/30 transition"
          >
            <Search className="w-5 h-5" />
            <span>Search & Add Courses</span>
            {/* Show appropriate chevron icon based on panel state */}
            {showCourseSearch ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>

        {/* Course Search Panel - only shown when showCourseSearch is true */}
        {showCourseSearch && (
          <div className="bg-white/5 border border-white/20 rounded-2xl p-6 mb-8 backdrop-blur-lg">
            <div className="flex items-center gap-4 mb-6">
              {/* Search input field */}
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Use Specific Course Names, ie. COMPSCI 300, ENGL 825, ISYE 823"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)} // Update search term state
                  className="w-full pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-400/50"
                />
              </div>
              {/* AI Auto-Fill button (placeholder functionality) */}
              <button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-6 py-3 rounded-xl transition font-medium">
                AI Auto-Fill Remaining
              </button>
            </div>
            
            {/* Grid of filtered course cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(searchTerm.trim() === ''
              ? filteredCourses.slice(0, 9) // Show only first 9 if no search
              : filteredCourses // Show all matches if searching
            ).map(course => (
              <CourseCard key={course.code} course={course} />
            ))}
          </div>
          </div>
        )}

        {/* Roadmap Timeline Section */}
        <div className="space-y-8">
          <h2 className="text-2xl font-bold text-white">Degree Timeline</h2>
          
        {/* Completed Courses Section */}
<div className="bg-green-500/5 border border-green-400/20 rounded-2xl p-6">
  <h3 className="text-xl font-semibold text-green-400 mb-6 flex items-center gap-2">
    <Check className="w-6 h-6" />
    Completed Courses
  </h3>
  {/* Horizontal scrollable container for semesters */}
  <div className="flex gap-8 overflow-x-auto snap-x snap-mandatory scroll-smooth pb-3 scrollbar-hide px-4">
    {/* Map through each semester of completed courses */}
    {Object.entries(completedCourses).map(([semester, courses]) => (
      <div key={semester}
        className="flex-shrink-0 w-[360px] snap-start bg-white/10 border border-white/20 rounded-xl p-6"  /* bigger width and padding */
      >
        <h4 className="text-xl font-medium text-white mb-4 text-center">{semester}</h4>
        <div className="space-y-4 pr-2">
          {/* Render each course in the semester */}
          {courses.map(course => (
            <CourseCard key={course.code} course={course} status="completed" />
          ))}
        </div>
      </div>
    ))}
  </div>
</div>

{/* Planned Courses Section */}
<div className="bg-blue-500/5 border border-blue-400/20 rounded-2xl p-8">  {/* increased padding */}
  <h3 className="text-xl font-semibold text-blue-400 mb-6 flex items-center gap-2">
    <Clock className="w-6 h-6" />  {/* slightly bigger icon */}
    Planned Courses
  </h3>

  <div className="flex gap-8 overflow-x-auto snap-x snap-mandatory scroll-smooth pb-3 scrollbar-hide px-4">
    {Object.entries(plannedCourses).map(([semester, courses]) => (
      <div
        key={semester}
        className="flex-shrink-0 w-[360px] snap-start bg-white/10 border border-white/20 rounded-xl p-6"  /* bigger width and padding */
      >
        <h4 className="text-xl font-medium text-white mb-4 text-center">{semester}</h4>  {/* bigger text */}
        <div className="space-y-4 pr-2">
        {courses.map((course) => (
        <CourseCard key={course.code} course={course} status="planned" />
  ))}
</div>

      </div>
    ))}
  </div>
</div>


          {/* Recommended CS Electives Section */}
          <div className="bg-purple-500/5 border border-purple-400/20 rounded-2xl p-6">
            <h3 className="text-xl font-semibold text-purple-400 mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Recommended CS Electives
            </h3>
            {/* Show first 3 courses from database as recommendations */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {courseDatabase.slice(0, 3).map(course => (
                <CourseCard key={course.code} course={course} />
              ))}
            </div>
            <div className="mt-4 text-center">
              <p className="text-gray-400 text-sm">
                Choose 2-3 electives to complete your degree requirements
              </p>
            </div>
          </div>
        </div>

         {/* Course Detail Modal - only renders when course is selected */}
    <CourseModal course={selectedCourse} onClose={() => setSelectedCourse(null)} />

<SemesterModal
  course={courseToAdd}
  plannedCourses={plannedCourses}
  completedCourses={completedCourses} // <-- add this line
  onClose={() => {
    setShowSemesterModal(false);
    setCourseToAdd(null);
  }}
  onAdd={handleAddCourse}
/>

    
      </div>
    </div>
    </div>
    </div>
  );
}