import React, {Component} from "react";
import {Breadcrumb} from "react-bootstrap";
import {includes, capitalize} from 'lodash';


export default class MyBreadcrumbs extends Component {
  onClick = (e) => {
    e.preventDefault();
    this.props.router.push(
        // Relative url
        e.currentTarget.getAttribute("href")
    );
  };

  cleanPathName = (path) => {
    if (includes(['boxes', 'versions', 'new', 'edit', 'account'], path)) {
      return capitalize(path);
    }
    return path;
  };

  renderRootBreadcrumb = () => {
    if (this.urlPathList.length >= 1) {
      return (
          <Breadcrumb.Item href="/" onClick={this.onClick}>
            Home
          </Breadcrumb.Item>
      );
    } else {
      return (
          <Breadcrumb.Item active>
            Home
          </Breadcrumb.Item>
      );
    }
  };

  renderRestBreadcrumbs = () => {
    const length = this.urlPathList.length;
    let url = '/';
    return this.urlPathList.map((path, index) => {
      if (index === length - 1) {
        return (
          <Breadcrumb.Item key={path} active>
            {this.cleanPathName(path)}
          </Breadcrumb.Item>
        );
      } else {
        url += `${path}/`;
        return (
          <Breadcrumb.Item key={path} href={url} onClick={this.onClick}>
            {this.cleanPathName(path)}
          </Breadcrumb.Item>
        );
      }
    });
  };

  render() {
    const location = this.props.router.getCurrentLocation().pathname;
    this.urlPathList = location.split('/').filter(p => p.length);
    return (
        <Breadcrumb>
          {this.renderRootBreadcrumb()}
          {this.renderRestBreadcrumbs()}
        </Breadcrumb>
    );
  }
}
