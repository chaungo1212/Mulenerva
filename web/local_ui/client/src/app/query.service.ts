/* This file was created by Patrick Shane McClintock in April 2018 for the Mulenerva Project. */

import { Injectable } from '@angular/core';

@Injectable()
export class QueryService {

  subject: string = "";
  query: string = "";
  filter: [boolean] = [true, true, true, true];
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

  isUpdated(): boolean {
    if (this.updated) {
      this.updated = false;
      return true;
    }
    else return false;
  }

  setFilter(filter: [boolean]): void {
    this.filter = filter;
    this.updated = true;
  }

  getFilter(): [boolean] {
    return this.filter;
  }
}
