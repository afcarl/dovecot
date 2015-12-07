#ifndef PARSEJSON_H
#define PARSEJSON_H

#include <string>
#include <vector>

#include <iostream>
#include <sstream>
#include <ctype.h>
#include <stack>
#include <stdexcept>
#include <boost/lexical_cast.hpp>
#include <boost/regex.hpp>
#include <unordered_map>

inline std::string getJSONString(std::istream& input_stream, bool remove_white_space)
{
  
  // 1) check if it starts with ", { or [
  // Remove whitespace at the front
  while (isspace(input_stream.peek()))
    input_stream.get();
  
  char c = input_stream.peek();
  if ( !( (c=='"') ||(c=='[') ||(c=='{') ) ) 
    throw std::runtime_error("JSON string should start with \" [ or {");

  c = input_stream.get();
  std::string json_string;
  json_string += c;
  
  std::stack<char> bracket_stack;
  // We know that the first character is ", [ or {
  bracket_stack.push(c);
  
  while (input_stream.good() && !bracket_stack.empty())
  {
    
    // Ignore whitespace
    if (remove_white_space)
      while (isspace(input_stream.peek()))
        input_stream.get();
    
    c = input_stream.get();
    //cout << "Before: " << c << " " << bracket_stack.top() << " " << json_string << " " << endl;
        
    json_string += c;

    if (c=='"') 
    {
      if (bracket_stack.top()=='"')
        bracket_stack.pop(); // Close string
      else
        bracket_stack.push(c); // Open string
    }
    else
    {
      if (bracket_stack.top()!='"') // Are we currently in a string element?
      {
        if (c=='{' || c=='[')
          bracket_stack.push(c);
  
        if (c=='}')
        {
          if (bracket_stack.top()=='{')
            bracket_stack.pop();
          else
            throw std::runtime_error("Closing bracket '}' does not have matching '{'");
        }
        
        if (c==']')
        {
          if (bracket_stack.top()=='[')
            bracket_stack.pop();
          else
            throw std::runtime_error("Closing bracket ']' does not have matching '['");
        }
      }
      
    }
    
    //char bst = (bracket_stack.empty()?'0':bracket_stack.top());
    //cout << "After : " << c << " " <<  bst << " " << json_string << " " << endl;
  }
  
  if (!bracket_stack.empty())
    throw std::runtime_error(std::string("Bracket '")+bracket_stack.top()+"' was not closed.");
    
  return json_string;
  
}

inline std::string getJSONValue(const std::string& str, const std::string& key)
{

  std::string regex_string = "\" *: *(.+?) *, *\"";
  std::string regex_string_last = "\" *: *(.+?) *\\}";
  boost::regex regex_name;
  boost::match_results<std::string::const_iterator> match;
  
  if(!boost::regex_search(str,match,boost::regex(key+regex_string)))
    if(!boost::regex_search(str,match,boost::regex(key+regex_string_last)))
      throw std::runtime_error("Could not find string '"+key+"'");
    
  return match[1];
}

/*
#include <vector>

int main()
{
  vector<string> input_strings;
  // Should be parseable
  input_strings.push_back("{Hello}World");
  input_strings.push_back("{He{ll}o}World");
  input_strings.push_back("{He[ll]o}World");
  input_strings.push_back("[He\"{l[l}\"o]World");
  input_strings.push_back("{H{{e}}l\"{l\"o}World");
  input_strings.push_back("{H{{e \n  }}l\"{l\"o}World");
  // Should NOT be parseable
  input_strings.push_back("Hello");
  input_strings.push_back("{Hello");
  input_strings.push_back("Hello}World");
  input_strings.push_back("{He]llo");
  input_strings.push_back("{He]llo");
  input_strings.push_back("\"{He]llo");
  
  for (unsigned int ii=0; ii<input_strings.size(); ii++)
  {
    cout << "______________________________________" << endl;
    cout << "  Input : '" << input_strings[ii] << "'" << endl;
    for (int no_white_space=1; no_white_space<=1; no_white_space++)
    {
      string json_string;
      stringstream string_stream(input_strings[ii]);
      try 
      {
        json_string = getJSONString(string_stream, no_white_space==1);
      } 
      catch (runtime_error rte)
      {
        cout << "    ERROR:" << rte.what() << endl;
      }
      
      string rest;
      while (string_stream.good())
        rest += string_stream.get();
      
      cout << "  Output: '" << json_string << "'" << endl;
      cout << "  Rest  : '" << rest << "'" << endl;
    }
  }
  
}
*/

#endif        //  #ifndef ParseJSON_H

