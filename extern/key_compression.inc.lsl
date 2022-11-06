#pragma once 

// Copyright (C) 2009 Adam Wozniak and Doran Zemlja
// Released into the public domain.
// Free for anyone to use for any purpose they like.
//
// deep voodoo base 4096 key compression
//
// It produces fixed length encodings of 11 characters.
// Salad Dais: Modified to handle non-UUID keys and
// compress NULL_KEY further
 
string str_replace(string subject, string search, string replace) {
   return llDumpList2String(llParseStringKeepNulls(subject, [search], []), replace);
}

string compress_key(key k) {
   if (k)
      ;
   else if (k == NULL_KEY)
      return "";
   else
      // specifically match invalid keys, just serialize as string.
      return "-" + (string)k;

   string s = llToLower(str_replace((string) k, "-", "") + "0");
   string ret;
   integer i;
 
   string A;
   string B;
   string C;
   string D;
 
   for (i = 0; i < 32; 0) {
      A = llGetSubString(s, i, i);
      i++;
      B = llGetSubString(s, i, i);
      i++;
      C = llGetSubString(s, i, i);
      i++;
      D = "b";
 
      if (A == "0") {
         A = "e";
         D = "8";
      }
      else if (A == "d") {
         A = "e";
         D = "9";
      }
      else if (A == "f") {
         A = "e";
         D = "a";
      }
 
      ret += "%e"+A+"%"+D+B+"%b"+C;
   }
   return llUnescapeURL(ret);
}
 
string pad_dash(string s) {
   return
      llGetSubString(s, 0, 7) + "-" +
      llGetSubString(s, 8,11) + "-" +
      llGetSubString(s,12,15) + "-" +
      llGetSubString(s,16,19) + "-" +
      llGetSubString(s,20,31);
}
 
key uncompress_key(string s) {
   // check for "-" prefix
   if (llGetSubString(s, 0, 0) == "-")
      // this is a tagged string-like key. Can't use -1 to mean the
      // end of the string because that will include the "-" if this is
      // a zero-length string.
      return (key)llGetSubString(s, 1, 0x7FffFFff);
   else if (s)
      ;
   else
      return NULL_KEY;

   integer i;
   string ret;
   string A;
   string B;
   string C;
   string D;
 
   s = llToLower(llEscapeURL(s));
   for (i = 0; i < 99; i += 9) {
      A = llGetSubString(s,i+2,i+2);
      B = llGetSubString(s,i+5,i+5);
      C = llGetSubString(s,i+8,i+8);
      D = llGetSubString(s,i+4,i+4);
 
      if (D == "8") {
         A = "0";
      }
      else if (D == "9") {
         A = "d";
      }
      else if (D == "a") {
         A = "f";
      }
      ret = ret + A + B + C;
   }
   return pad_dash(ret);
}
