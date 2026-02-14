"use client";
import { useState, useEffect, useRef } from "react";

export default function Autocomplete({
    placeholder = "Search...",
    apiEndpoint,
    selectedValues = [],
    onChange,
    className = ""
}) {
    const [inputValue, setInputValue] = useState("");
    const [options, setOptions] = useState([]);
    const [filteredOptions, setFilteredOptions] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [dropdownAbove, setDropdownAbove] = useState(false); // Smart positioning
    const wrapperRef = useRef(null);
    const inputRef = useRef(null);

    // Fetch options from API
    useEffect(() => {
        async function fetchOptions() {
            setLoading(true);
            try {
                const response = await fetch(apiEndpoint);
                if (response.ok) {
                    const data = await response.json();
                    setOptions(data);
                    setFilteredOptions(data);
                }
            } catch (error) {
                console.error("Error fetching autocomplete options:", error);
            } finally {
                setLoading(false);
            }
        }
        fetchOptions();
    }, [apiEndpoint]);

    // Filter options based on input
    useEffect(() => {
        if (inputValue.trim() === "") {
            setFilteredOptions(options);
        } else {
            const filtered = options.filter((option) =>
                option.toLowerCase().includes(inputValue.toLowerCase())
            );
            setFilteredOptions(filtered);
        }
    }, [inputValue, options]);

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Smart positioning - flip dropdown above if not enough space below
    useEffect(() => {
        if (isOpen && wrapperRef.current) {
            const rect = wrapperRef.current.getBoundingClientRect();
            const viewportHeight = window.innerHeight;
            const spaceBelow = viewportHeight - rect.bottom;
            const dropdownHeight = 320; // max-h-80 = 320px

            // If not enough space below, position above
            if (spaceBelow < dropdownHeight && rect.top > dropdownHeight) {
                setDropdownAbove(true);
            } else {
                setDropdownAbove(false);
            }
        }
    }, [isOpen]);

    function handleInputChange(e) {
        setInputValue(e.target.value);
        setIsOpen(true);
    }

    function handleInputFocus() {
        setIsOpen(true);
    }

    function handleOptionClick(option) {
        // Add to selected values if not already selected
        if (!selectedValues.includes(option)) {
            onChange([...selectedValues, option]);
        }
        setInputValue("");
        setIsOpen(false);
        inputRef.current?.focus();
    }

    function handleRemoveChip(value) {
        onChange(selectedValues.filter((v) => v !== value));
    }

    function handleKeyDown(e) {
        // Remove last chip on backspace if input is empty
        if (e.key === "Backspace" && inputValue === "" && selectedValues.length > 0) {
            onChange(selectedValues.slice(0, -1));
        }
        // Close dropdown on Escape
        if (e.key === "Escape") {
            setIsOpen(false);
        }
    }

    return (
        <div ref={wrapperRef} className={`relative ${className}`}>
            {/* Input and Chips Container */}
            <div className="h-[50px] overflow-y-auto bg-white/5 border border-white/20 rounded-lg px-3 py-2 flex flex-wrap gap-2 items-center focus-within:border-cyan-400 transition content-start">
                {/* Selected chips */}
                {selectedValues.map((value) => (
                    <div
                        key={value}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-gradient-to-r from-cyan-500/20 to-purple-600/20 border border-cyan-400/50 rounded-md text-sm text-white"
                    >
                        <span>{value}</span>
                        <button
                            type="button"
                            onClick={() => handleRemoveChip(value)}
                            className="hover:text-red-400 transition"
                        >
                            ×
                        </button>
                    </div>
                ))}

                {/* Input field */}
                <input
                    ref={inputRef}
                    type="text"
                    value={inputValue}
                    onChange={handleInputChange}
                    onFocus={handleInputFocus}
                    onKeyDown={handleKeyDown}
                    placeholder={selectedValues.length === 0 ? placeholder : ""}
                    className="flex-1 min-w-[120px] bg-transparent text-white placeholder-slate-400 outline-none"
                />
            </div>

            {/* Dropdown */}
            {isOpen && (
                <div className={`absolute z-[9999] w-full max-h-80 overflow-y-auto bg-slate-800/95 backdrop-blur-md border border-white/20 rounded-lg shadow-xl ${dropdownAbove ? 'bottom-full mb-2' : 'top-full mt-2'
                    }`}>
                    {loading ? (
                        <div className="px-4 py-3 text-slate-400 text-sm">Loading...</div>
                    ) : filteredOptions.length === 0 ? (
                        <div className="px-4 py-3 text-slate-400 text-sm">No options found</div>
                    ) : (
                        <div className="py-2">
                            {filteredOptions.map((option, index) => {
                                const isSelected = selectedValues.includes(option);
                                return (
                                    <button
                                        key={index}
                                        type="button"
                                        onClick={() => handleOptionClick(option)}
                                        disabled={isSelected}
                                        className={`w-full px-4 py-2 text-left text-sm transition ${isSelected
                                            ? "bg-cyan-500/10 text-cyan-400 cursor-not-allowed"
                                            : "text-white hover:bg-white/10 cursor-pointer"
                                            }`}
                                    >
                                        {isSelected && <span className="mr-2">✓</span>}
                                        {option}
                                    </button>
                                );
                            })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
