import React, {Component} from "react";
import {ListGroup, ListGroupItem} from "react-bootstrap";
import Moment from "moment";
import BoxOrdering from "./BoxOrdering";
import MyPagination from "./MyPagination";
import MySpinner from "./MySpinner";


export default class BoxList extends Component {
  onBoxClick = (e) => {
    e.preventDefault();
    this.props.router.push(
        // Relative url
        e.currentTarget.getAttribute("href")
    );
    return false;
  };

  renderBoxesList = () => {
    return this.boxTags.map(tag => {
      const box = this.props.boxes[tag];
      return (
          <ListGroupItem
              key={box.tag}
              href={`/boxes/${box.tag}`}
              onClick={this.onBoxClick}
          >
            <div>
              <h4>{box.tag}</h4>
              <p>{box.short_description}</p>
            </div>
            <div>{box.pulls} pulls</div>
            <small title={Moment(box.date_updated).format('LLL')}>
              Last updated: {Moment(box.date_updated).fromNow()}
            </small>
          </ListGroupItem>
      );
    });
  };

  renderPagination = () => {
    if (this.boxPages.count <= 10) {
      return null;
    }
    return (
        <MyPagination
            router={this.props.router}
            itemsCount={this.boxPages.count}
        />
    );
  };

  renderList = () => {
    if (!this.boxPages || !this.boxTags.length) {
      return <MySpinner />;
    }

    if (this.boxPages.count === 0) {
      return <p>No boxes</p>
    }

    return (
        <div>
          <ListGroup>
            {this.renderBoxesList()}
          </ListGroup>
          {this.renderPagination()}
        </div>
    )
  };

  render() {
    this.activePage = parseInt(this.props.router.location.query.page || 1, 10);
    this.boxPages = this.props.boxesPages;
    this.boxTags = (this.boxPages && this.boxPages.pages[this.activePage]) || [];
    return (
        <div>
          <BoxOrdering router={this.props.router} />
          {this.renderList()}
        </div>
    );
  }
}
