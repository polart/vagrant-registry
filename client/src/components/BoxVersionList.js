import React, {Component} from "react";
import { connect } from 'react-redux';
import {Pagination, ListGroup, ListGroupItem, Label} from 'react-bootstrap';
import Moment from 'moment';
import * as actions from "../actions";


class BoxVersionList extends Component {
  state = {
    page: 1,
  };

  componentDidMount() {
    this.props.fetchBoxVersions(this.props.boxTag, this.state.page);
  }

  onPageChange = (page) => {
    this.props.fetchBoxVersions(this.props.boxTag, page);
    this.setState({page});
  };

  onBoxVersionClick = (e) => {
    e.preventDefault();
    this.props.router.push(
        // Relative url
        e.currentTarget.getAttribute("href")
    );
    return false;
  };

  renderPagination = () => {
    if (!this.props.boxVersionsPages) {
      return;
    }

    if (this.props.boxVersionsPages.count <= 10) {
      return null;
    }

    const items = Math.ceil(this.props.boxVersionsPages.count / 10);
    return (
        <Pagination
            prev
            next
            first
            last
            ellipsis
            boundaryLinks
            items={items}
            maxButtons={5}
            activePage={this.state.page}
            onSelect={this.onPageChange}
        />
    );
  };

  renderProviders = (version) => {
    return version.providers.map((providerTag) => {
      const provider = this.props.boxProviders[providerTag];
      return (
          <span key={providerTag} >
            <Label bsStyle="primary">
              {provider.provider}
            </Label>
            &nbsp;
          </span>
      );
    });
  };

  renderVersionsList = () => {
    if (!this.props.boxVersionsPages) {
      return;
    }

    const versionTags = this.props.boxVersionsPages.pages[this.state.page];
    if (!versionTags) {
      return;
    }

    return versionTags.map(tag => {
      const version = this.props.boxVersions[tag];
      return (
          <ListGroupItem
              key={version.version}
              href={`/boxes/${this.props.boxTag}/versions/${version.version}/`}
              onClick={this.onBoxVersionClick}
          >
            <h4 className="list-group-item-heading">
              v{version.version} |&nbsp;
              <small title={Moment(version.date_updated).format('LLL')}>
                Last updated: {Moment(version.date_updated).fromNow()}
              </small>
            </h4>
            <p>Initial release</p>
            {this.renderProviders(version)}
          </ListGroupItem>
      );
    });
  };

  renderVersions = () => {
    // if (!this.props.box) {
    //   return <div>Loading...</div>
    // }

    return (
      <div>
        <ListGroup>
          {this.renderVersionsList()}
        </ListGroup>
        {this.renderPagination()}
      </div>
    );
  };

  render() {
    return (
        <div>
          {this.renderVersions()}
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    boxVersions: state.entities.boxVersions,
    boxVersionsPages: state.pagination.boxVersions[props.boxTag],
    boxProviders: state.entities.boxProviders,
  };
}

export default connect(mapStateToProps, {
  fetchBoxVersions: actions.loadBoxVersions,
})(BoxVersionList)
