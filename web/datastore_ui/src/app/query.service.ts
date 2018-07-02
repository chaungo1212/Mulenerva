import { Injectable } from '@angular/core';

@Injectable()
export class QueryService {

  subject: string = ""; 
  query: string = "";
  updated: boolean = false;

  constructor() { }

  setSubject(subject: string): void {
    this.subject = subject;
    this.updated = true;
  }

  getSubject(): string  {
    return this.subject;
  }

 

  setQuery(query: string): void {
    this.query = query;
    this.updated = true;
  }

  getQuery(): string {
    return this.query;
  }


  
}